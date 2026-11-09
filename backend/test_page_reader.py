from app.services.page_readers import read_page

url = "https://example.com"

text = read_page(url)

print("PAGE TEXT:")
print(text[:3000])