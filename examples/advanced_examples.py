"""Advanced usage examples with nested structures and complex schemas"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from auto_structured_output import StructureExtractor

# Initialize OpenAI client
load_dotenv(".envrc")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the structure extractor
extractor = StructureExtractor(client)


def run(prompt: str, file_name: str):
    T_Model = extractor.extract_structure(prompt)

    print(f"Generated model: {T_Model.__name__}")
    print(f"Fields: {T_Model.model_json_schema()}")

    # Use the model
    response = client.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format=T_Model,
    )

    data = response.choices[0].message.parsed
    data_dict = data.model_dump()
    print("\nGenerated data:")
    print(data_dict)

    extractor.save_extracted_json(T_Model, file_name)


def example_1_nested_objects():
    """Example 1: Nested object structures"""
    print("\n=== Example 1: Nested Objects (User Profile) ===")

    prompt = """You are an expert at extracting data from user profile.
<user_profile>
John Doe is a software engineer from San Francisco, CA. He loves hiking and photography.
He can be reached at email: johndoe@example.com
He prefers the dark theme and has enabled email notifications. Also, he speaks English and Spanish.
His avatar URL is https://example.com/avatar/johndoe.jpg
His user ID is user_12345 and username is johndoe.
In his settings, he has chosen the dark theme, enabled notifications, and set his preferred language to English (en).
</user_profile>    

Output user profile information:
- user_id
- username
- email
- profile
  - first_name
  - last_name
  - bio
  - avatar_url
- settings
  - theme
  - notifications_enabled
  - language
    """

    run(prompt, "examples/schemas/advanced_examples/user_profile.json")


def example_2_complex_article():
    """Example 2: Complex article with nested author and comments"""
    print("\n=== Example 2: Complex Article Structure ===")

    prompt = """Your task is to extract structured information from an article.
You are an expert at defining complex data models with nested objects and arrays.

<article>
Understanding AI and Its Impact on Society
Artificial Intelligence (AI) is transforming the way we live and work. From healthcare to transportation, AI technologies are being integrated into various sectors, leading to increased efficiency and new opportunities. However, the rise of AI also raises ethical concerns, including job displacement and privacy issues. As we continue to develop AI, it is crucial to consider its societal implications and ensure that its benefits are widely shared.
Author: Jane Smith
Email: janesmith@example.com
Bio: Jane is a tech journalist with over 10 years of experience covering AI and emerging technologies.
Website: https://janesmith.tech
Tags: AI, technology, society, ethics
Published At: 2024-05-15T10:00:00Z
Status: published
Views: 1500
Likes: 300
Comments Count: 45
</article>
       
Output article information:
- article_id
- title
- body: Article content
- author:
  - author_id: Author ID
  - name
  - email
  - profile:
    - bio
    - website: Author website URL
- tags: Article tags
- published_at
- status: "draft", "published", or "archived"
- metadata:
  - views
  - likes
  - comments_count
    """

    run(prompt, "examples/schemas/advanced_examples/complex_article.json")


def example_3_array_of_objects():
    """Example 3: Arrays of nested objects"""
    print("\n=== Example 3: Array of Objects (Order System) ===")

    prompt = """You are an expert at defining complex data models with nested objects and arrays.
Read the following order information and extract structured data.
<order>
Order ID: order_98765
Customer Name: Alice Johnson
Order Date: 2024-06-01T14:30:00Z
Items:
1. Product ID: prod_001, Product Name: Laptop, Quantity: 1, Unit Price: 999.99
2. Product ID: prod_002, Product Name: Mouse, Quantity: 2, Unit Price: 25.50
3. Product ID: prod_003, Product Name: Keyboard, Quantity: 1, Unit Price: 45.00
Shipping Address:
Street: 123 Main St
City: Springfield
State: IL
Postal Code: 62701
Country: USA
Total Amount: 1096.99
Status: shipped
</order>
    
The output should be in the following format:
- order_id
- customer_name
- order_date
- items list:
  - product_id
  - product_name
  - quantity
  - unit_price
  - subtotal
- shipping_address
  - street
  - city
  - state
  - postal_code
  - country
- total_amount
- status: "pending", "processing", "shipped", or "delivered"
    """

    run(prompt, "examples/schemas/advanced_examples/order_system.json")


def example_4_deep_nesting():
    """Example 4: Deeply nested structure (Organization)"""
    print("\n=== Example 4: Deeply Nested Structure (Organization) ===")

    prompt = """
Output organization information:
- org_id (string): Organization ID
- name (string): Organization name
- departments (array of objects):
  - dept_id (string): Department ID
  - dept_name (string): Department name
  - manager (object):
    - employee_id (string): Manager's employee ID
    - name (string): Manager's name
    - email (string): Manager's email
  - teams (array of objects):
    - team_id (string): Team ID
    - team_name (string): Team name
    - members (array of objects):
      - employee_id (string): Employee ID
      - name (string): Employee name
      - role (string): Employee role
      - email (string): Employee email
    """

    run(prompt, "examples/schemas/advanced_examples/organization.json")


def example_5_anyof_union_types():
    """Example 5: Using anyOf for union types"""
    print("\n=== Example 5: Union Types (Payment Methods) ===")

    prompt = """ Your task is to define a data model for payment information.
Analyze the following payment details and extract structured data.
<payment>
Payment ID: pay_54321
Amount: 150.75
Currency: USD
Payment Method: Credit Card
Card Number: 4111 1111 1111 1111
Expiry Date: 12/26
CVV: 123
Status: completed
Timestamp: 2024-06-10T09:15:00Z
</payment>
    
Output payment information:
- payment_id (string): Unique payment identifier
- amount (number): Payment amount
- currency (string): Currency code (e.g., USD, EUR)
- payment_method (object with anyOf):
  Either credit card with:
    - type: "credit_card"
    - card_number (string): Card number
    - expiry_date (string): Expiry date
    - cvv (string): CVV code
  Or bank transfer with:
    - type: "bank_transfer"
    - account_number (string): Bank account number
    - routing_number (string): Routing number
    - bank_name (string): Bank name
  Or digital wallet with:
    - type: "digital_wallet"
    - wallet_provider (string): Provider name (e.g., PayPal, Venmo)
    - wallet_id (string): Wallet ID
- status (enum): Payment status - "pending", "completed", or "failed"
- timestamp (datetime): Payment timestamp
    """

    run(prompt, "examples/schemas/advanced_examples/payment_methods.json")


def example_6_validation_constraints():
    """Example 6: Models with validation constraints"""
    print("\n=== Example 6: Validation Constraints ===")

    prompt = """<role>You are an expert at defining data models with validation constraints.</role>
<instruction>Extract product information from the following text.</instruction>
<product>
Product SKU: ABC-1234
Name: Ultra HD 4K TV
Price: 799.99
Stock Quantity: 50
Weight: 15.5 kg
Dimensions: 123.5 cm x 75.0 cm x 8.0 cm
Tags: electronics, TV, 4K, UHD
</product>
    
Output product specification:
- sku (string): Stock keeping unit (pattern: [A-Z]{3}-[0-9]{4})
- name (string): Product name
- price (number): Price (minimum: 0.01, maximum: 999999.99)
- stock_quantity (integer): Stock quantity (minimum: 0)
- weight_kg (number): Weight in kilograms (minimum: 0, multiple of 0.01)
- dimensions (object):
  - length_cm (number): Length in cm (minimum: 0.1)
  - width_cm (number): Width in cm (minimum: 0.1)
  - height_cm (number): Height in cm (minimum: 0.1)
- tags (array of strings): Product tags (minimum items: 1, maximum items: 10)
    """

    run(prompt, "examples/schemas/advanced_examples/product_specification.json")


if __name__ == "__main__":
    print("Auto-Structured-Output: Advanced Examples")
    print("=" * 60)

    example_1_nested_objects()
    example_2_complex_article()
    example_3_array_of_objects()
    example_4_deep_nesting()
    example_5_anyof_union_types()
    example_6_validation_constraints()

    print("\n" + "=" * 60)
    print("All advanced examples completed successfully!")
