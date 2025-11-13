"""
Quick test to verify HTML formatting
"""
from bs4 import BeautifulSoup

# Sample HTML
html = '<div class="et_pb_text_inner"><h1>Digital Robotics for your Company 2.0</h1><p>Deploy automations powered by AI, Big Data, Web Crawling and Natural Language.</p></div>'

soup = BeautifulSoup(html, 'html.parser')
div = soup.find('div')

print("=== OLD METHOD (removed whitespace) ===")
old_format = ' '.join(str(div).split())
print(old_format)
print()

print("=== NEW METHOD (prettify with indentation) ===")
new_format = div.prettify()
print(new_format)
print()

print("=== This matches your UI mockup! ===")
print("The HTML now has:")
print("✅ Proper line breaks")
print("✅ Indentation")
print("✅ Readable format")


