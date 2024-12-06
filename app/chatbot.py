from flask import Blueprint, request, jsonify, session
# from flask_login import current_user
import logging
from openai import OpenAI

from .models.product import Product

bp = Blueprint('chatbot', __name__)

# get api_key from env
import os
api = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=api
)

def generate_gpt_response(messages):
    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "I'm sorry, I'm having trouble processing your request right now."

def generate_follow_up_response(messages, product_info):
    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages=messages,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "I'm sorry, I'm having trouble processing your request right now."

FOLLOWUP_SYSTEM_PROMPT = (
    "You are assisting the user with follow-up questions about a specific product they have inquired about. "
    "Provide detailed and accurate information based on the available product data. If the user asks for details such as the seller, reviews, description, price, or any other product-related information, respond accordingly. "
    "Maintain the context of the conversation and ensure that your responses are clear and helpful. "
    "At NO point should you invent information about a product."
    "If you are unsure about the user's request, ask for clarification."
    "EXAMPLES:\n"
    "- *User*: Who is selling this product?\n"
    "- *You*: The product is sold by multiple sellers: <a href='/user/(id)'>Alice Johnson</a>, <a href='/user/(id)'>Bob Smith</a>, and <a href='/user/(id)'>Charlie Brown</a>.\n\n"
    "- *User*: What is the average review score for this product?\n"
    "- *You*: The average review score for this product is 4.5 based on 100 reviews.\n\n"
    "- *User*: Can you tell me more about this product?\n"
    "- *You*: Sure! This product is a high-quality item with a durable design and advanced features. It is available in multiple colors and sizes. You can see more info <a href='/products/(id)'>here</a>.\n\n"
    "Remember to provide accurate and relevant information to assist the user with their follow-up questions."
    "Here is the product information:"
)

SYSTEM_PROMPT = (
    "You are a highly intelligent and interactive chatbot for an online shopping website. "
    "Do not format your response in any way, so do not use stars for bolding or underscores for italics, etc.... "
    "Your primary goal is to assist users in finding products and navigating various sections of the website. \n"
    "You have 3 reply options: 'LOOKUP: (keywords)', 'INFO', and a general response.\n"
    "You can detect when a user intends to search for a product, in which case your reply with 'LOOKUP: (keywords)', where keywords is a string of words that the user is looking for.\n\n"
    "At NO point should you invent information about a product. Always reply with 'LOOKUP: (keywords)' to get the most relevant product.\n\n"
    "You can aslo detect when a user intends to ask a follow up about the product, in which case you should reply with just 'INFO', even if you don't know what product they're referring to. Follow ups include questions about who is selling the product, its reviews, description, price....\n\n"
    "The product can be vague, such as 'car seat' or 'laptop', or more specific. However, if the query is blatantly irrelevant, such as 'Look up a akjsdhfjkashdf', you should respond with a message asking for clarification.\n\n"
    "If the message is clearly irrelevant to an online shopping context, respond with instructions of what you can do.\n\n"
    "**Available Product Information:**\n"
    "- `product_id`\n"
    "- `category_name`\n"
    "- `name`\n"
    "- `description`\n"
    "- `image_url`\n"
    "- `price`\n"
    "- `created_by`\n"
    "- `relevance`\n"
    "- `avg_review_score`\n"
    "- `review_count`\n\n"
    "**Website Pages and Their Functions:**\n"
    "- `/`: Home page.\n"
    "- `/account`: View basic account information.\n"
    "- `/edit_account`: Edit name, address, and manage account balance (top up/withdraw).\n"
    "- `/purchase_history`: View past purchases, order statuses, and add reviews to eligible orders.\n"
    "- `/reviewsrecent`: View and edit recent reviews.\n"
    "- `/seller_profile`: For sellers to view stats like total sales, average review rating, total orders, manage inventory, create new listings, and view current orders.\n"
    "- `/view_inventory`: View and edit current inventory items.\n"
    "- `/view_orders`: View pending, processing, and completed orders.\n"
    "- `/cart`: View items in the cart and items saved for later.\n\n"
    "**Guidelines:**\n"
    "1. **Intent Detection**: Determine whether the user wants to perform a product search. Look for keywords and phrases indicating a search intent, such as 'look up,' 'find,' 'search for,' 'show me,' etc.\n"
    "2. **Product Searches**: When a product search is detected, use `Products.best_search_by_keyword` to retrieve relevant products. Provide detailed information including name, description, price, image, average review score, and review count.\n"
    "3. **Account Management**: Assist users in navigating to account-related pages, help with editing account details, and managing their balance.\n"
    "4. **Order and Purchase History**: Help users view their past orders, check order statuses, and add reviews to purchases.\n"
    "5. **Seller Functions**: Guide sellers in managing their profiles, inventory, and orders.\n"
    "6. **Navigation Assistance**: Help users navigate to different sections of the website by providing direct links or instructions.\n"
    "7. **Maintain Context**: Keep track of the conversation context to provide coherent and relevant responses.\n"
    "8. **Politeness and Clarity**: Always communicate politely, clearly, and concisely. If unsure about a user's request, ask for clarification.\n"
    "9. **Security and Privacy**: Do not request or expose sensitive information. Guide users to appropriate pages for sensitive actions.\n\n"
    "**Example Interactions:**\n"
    "- *User*: Hi\n"
    "- *You*: Hello! I'm your shopping assistant. How can I help you today?\n\n"
    "- *User*: Can I update my address?\n"
    '- *You*: Absolutely! You can update your address by visiting the <a href="/edit_account">Edit Account</a> page.\n\n'
    "- *User*: Show me my recent purchases.\n"
    '- *You*: You can find your recent purchases <a href="/purchase_history">here</a>.\n\n'
    "- *User*: I'm a seller, how can I manage my inventory?\n"
    '- *You*: You can manage your inventory by visiting the <a href="/view_inventory">inventory page</a>.\n\n'
    "Feel free to ask me anything related to shopping, account management, or navigating our website!"
)

def is_product_search(message):
    return message.startswith("LOOKUP:")

def is_follow_up(message):
    return message.startswith("INFO")

@bp.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    logging.debug(f"Received message: {user_message}")
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    if 'conversation' not in session:
        session['conversation'] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    session['conversation'].append({"role": "user", "content": user_message})

    response = generate_gpt_response(session['conversation'])

    if is_product_search(response):
        logging.debug("Product search intent detected.")

        # Extract keywords from user message
        lookup = response.replace("LOOKUP:", "").strip().lower()
        products = Product.best_search_by_keyword(lookup)
        if products:
            top_product = products

            message = f"Here is what I found for {lookup}:"

            product_display = (
                f"<div style='border: 1px solid #ddd; padding: 10px; margin: 10px 0;'>"
                f"<h5>{top_product['name']}</h5>"
                f"<p><strong>Category:</strong> {top_product['category_name']}</p>"
                f"<p><strong>Price:</strong> ${top_product['price']}</p>"
                f"<p><img src='{top_product['image_url']}' alt='{top_product['name']}' style='max-width: 100%; height: auto;'></p>"
            )

            if top_product['review_count'] > 0:
                product_display += f"<p><strong>Review Score:</strong> {str(round(float(top_product['avg_review_score']), 2))} ({top_product['review_count']})</p>"
            
            product_display +=  (f"<p><a href='/products/{top_product['product_id']}' style='color: #007bff; text-decoration: none;'>View Product</a></p>"
                f"<p>How can I assist you further with this product?</p>"
                f"</div>")

            message += "\n" + product_display
            assistant_response = message
            session['conversation'].append({"role": "assistant", "content": assistant_response})
            session['selected_product_id'] = top_product['product_id']
            session.modified = True
            return jsonify({'response': assistant_response})
        else:
            assistant_response = "I'm sorry, I couldn't find any products matching your description. Could you please provide more details or try different keywords?"
            session['conversation'].append({"role": "assistant", "content": assistant_response})
            session.modified = True
            return jsonify({'response': assistant_response})

    elif is_follow_up(response):
        if not session.get('selected_product_id'):
            assistant_response = "I'm sorry, I don't have a product to provide information for. Could you please search for a product first?"
            session['conversation'].append({"role": "assistant", "content": assistant_response})
            session.modified = True
            return jsonify({'response': assistant_response})
        content = FOLLOWUP_SYSTEM_PROMPT + "Product info:\n"

        top_product = Product.get(session['selected_product_id'])

        top_product = Product.to_dict(top_product)


        info = Product.get_all_info_by_id(top_product['product_id'])

        # Retrieve individual product info from session
        product_info = {
            "product_id": top_product['product_id'],
            "category_name": info.get('category_name'),
            "name": info.get('name'),
            "description": info.get('description'),
            "price": info.get('price'),
            "image_url": info.get('image_url'),
            "reviews": info.get('reviews', []),
            "inventory": info.get('inventory'),
            "sellers": info.get('sellers', [])
        }

        product_info_str = ""
        for key, value in product_info.items():
            if isinstance(value, list):
                value = ', '.join(str(item) for item in value)
            product_info_str += f"{key}: {value}\n"
        content += product_info_str

        followup_message = [
            {"role": "system", "content": content},
            {"role": "user", "content": user_message}
        ]

        new_response = generate_follow_up_response(followup_message, product_info)

        session['conversation'].append({"role": "assistant", "content": new_response})
        session.modified = True

        return jsonify({'response': new_response})

    else:
        session['conversation'].append({"role": "assistant", "content": response})
        session.modified = True
        return jsonify({'response': response})

@bp.route('/reset_chatbot_session', methods=['POST'])
def reset_chatbot_session():
    session.pop('selected_product_id', None)
    session.pop('conversation', None)
    logging.debug("Chatbot session has been reset.")
    return jsonify({'status': 'Chatbot session reset.'}), 200