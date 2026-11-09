from datetime import datetime, timedelta
import os
import random
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserLogin, OTPVerify

# Load environment variables
load_dotenv()

# Gmail SMTP settings
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "hackmate-secret"
)

ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)


def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(
        minutes=int(
            os.getenv(
                "ACCESS_TOKEN_EXPIRE_MINUTES",
                "60"
            )
        )
    )

    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# -----------------------------
# SEND OTP EMAIL
# -----------------------------

def send_otp_email(receiver_email: str, verification_code: str):

    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        raise RuntimeError(
            "SMTP_EMAIL or SMTP_APP_PASSWORD is not configured"
        )

    message = EmailMessage()

    message["Subject"] = "HackMates Email Verification OTP"
    message["From"] = SMTP_EMAIL
    message["To"] = receiver_email

    message.set_content(
        f"""
Hello,

Welcome to HackMates!

Your email verification OTP is:

{verification_code}

This OTP is required to verify your HackMates account.

If you did not create a HackMates account, you can ignore this email.

Regards,
HackMates Team
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(
            SMTP_EMAIL,
            SMTP_APP_PASSWORD
        )
        server.send_message(message)

def send_chat_message_email(
    receiver_email: str,
    sender_name: str,
    message_content: str
):
    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        raise RuntimeError(
            "SMTP_EMAIL or SMTP_APP_PASSWORD is not configured"
        )

    message = EmailMessage()

    message["Subject"] = f"New message from {sender_name} - HackMates"
    message["From"] = SMTP_EMAIL
    message["To"] = receiver_email

    message.set_content(
        f"""
Hello,

You have received a new message on HackMates.

From: {sender_name}

Message:
{message_content}

Open HackMates to reply to this message.

Regards,
HackMates Team
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(
            SMTP_EMAIL,
            SMTP_APP_PASSWORD
        )
        server.send_message(message)
# -----------------------------
# REGISTER
# -----------------------------

@router.post("/register")
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    if db.query(User).filter(
        User.email == user_data.email
    ).first():

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Generate 6-digit OTP
    verification_code = str(
        random.randint(100000, 999999)
    )

    # Create user
    user = User(
        name=user_data.name,
        email=user_data.email,
        is_email_verified=False,

        verification_code_hash=pwd_context.hash(
            verification_code
        ),

        password=pwd_context.hash(
            user_data.password
        ),

        skills=",".join(user_data.skills),
        roles=",".join(user_data.roles),
        interests=",".join(user_data.interests),

        rating=0.0
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Send OTP to user's email
    try:

        send_otp_email(
            user.email,
            verification_code
        )

    except Exception as error:

        # Remove user if email could not be sent
        db.delete(user)
        db.commit()

        print("OTP email error:", error)

        raise HTTPException(
            status_code=500,
            detail="Could not send verification email"
        )

    # IMPORTANT:
    # Do not return the OTP to the frontend.
    return {
        "message": "Registration successful. Verification OTP sent to your email.",
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email
    }


# -----------------------------
# LOGIN
# -----------------------------

@router.post("/login")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    if not user or not pwd_context.verify(
        login_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.is_email_verified:

        raise HTTPException(
            status_code=403,
            detail="Please verify your email first"
        )

    return {
    "message": "Login successful",

    "access_token": create_access_token(
        user.user_id
    ),

    "token_type": "bearer",

    "user_id": user.user_id,

    "name": user.name,

    "email": user.email,

    "skills": [
        skill.strip()
        for skill in (user.skills or "").split(",")
        if skill.strip()
    ],

    "roles": [
        role.strip()
        for role in (user.roles or "").split(",")
        if role.strip()
    ],

    "interests": [
        interest.strip()
        for interest in (user.interests or "").split(",")
        if interest.strip()
    ],

    "rating": user.rating or 0
}
# -----------------------------
# VERIFY OTP
# -----------------------------

@router.post("/verify-otp")
def verify_otp(
    otp_data: OTPVerify,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.user_id == otp_data.user_id
    ).first()

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_email_verified:

        return {
            "message": "Email already verified"
        }

    if not user.verification_code_hash:

        raise HTTPException(
            status_code=400,
            detail="No verification code found"
        )

    # Verify OTP
    if not pwd_context.verify(
        otp_data.verification_code,
        user.verification_code_hash
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )

    # Mark email as verified
    user.is_email_verified = True

    # Remove OTP hash after successful verification
    user.verification_code_hash = None

    db.commit()

    return {
        "message": "Email verified successfully",
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email
    }