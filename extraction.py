import re
import os
import GroceryItem

# FIRST_PARSER = r'([0-9]\.|\.[0-9]|[0-9],|,[0-9])'
PRICE_PARSER = r'[a-zA-Z]\s.*(\.[0-9]|,[0-9]).*[a-zA-Z]'
STATS_FILTER = ["perk", "tax", "visa", "change", "balance"]

# TODO - detect total amount and select the discounted one
# might also need an undiscounted one for comparing with the sum
# try use priority dict 
# Detect weighted items

def is_item(text):
    text = text.lower()
    for word in STATS_FILTER:
        if word in text:
            return False
        
    return True

def parse_item_line(text):
    text = text.replace(",", ".")
    if '@' in text:
        pass

    item_name = None
    item_price = None
    text_arr = text.split()
    for i in range(len(text_arr)):
        if re.search(r'(\.[0-9]|,[0-9])', text_arr[i]) != None:
            item_name = " ".join(text_arr[:i])
            item_price = parse_price(text_arr[i])
            break

    if item_name is None or item_price is None:
        return "Not found"
    return item_name, str(item_price)

    
def parse_price(price_text):
    rgx = r'[0-9]*\.[0-9][0-9]'
    pos_neg = 1
    result = re.search(rgx, price_text)
    next_index = result.end()
    if (next_index < len(price_text)
        and price_text[next_index] == '-'):

        pos_neg *= -1

    return float(result.group()) * pos_neg


def get_store_name(texts):
    for text in texts:
        lowered = text.lower()
        if "aldi" in lowered:
            return "ALDI"
        if "district" in lowered:
            return "GE"
        
    return "Unknown"


def parse(texts):
    # Get store name
    # store_name = get_store_name(texts[:10])

    result = []

    for text in texts:
        if (re.search(PRICE_PARSER, text) != None
            and is_item(text)):
            result.append(parse_item_line(text))

    return [f'{item},{price}\n' for item, price in result]


if __name__ == "__main__":


    text_files = os.listdir('text')
    
    for text_file in text_files:
        print('='*20)
        print('='*5 + text_file + '='*5)
        text = ''
        with open('text/'+text_file) as file:
            texts = file.readlines()

        result = parse(texts)
        for item, price in result:
            print(f'{item},{price}')


