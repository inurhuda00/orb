import json
import os

def store_order(action, interval, ticker, exchange, ticket):
    order_data = {
        "action": action,
        "interval": interval,
        "ticker": ticker,
        "exchange": exchange,
        "ticket": ticket
    }

    filename = 'orders.json'
    with open(filename, 'a') as file:
        json.dump(order_data, file)
        file.write('\n')


def find_order_by_criteria(interval, ticker, exchange):
    criteria = {
        "interval": interval,
        "ticker": ticker,
        "exchange": exchange
    }

    found_orders = []
    filename = 'orders.json'
    with open(filename, 'r') as file:
        for line in file:
            try:
                order_data = json.loads(line)
                if all(order_data.get(key) == value for key, value in criteria.items()):
                    found_orders.append(order_data)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line.strip()}")

    return found_orders

def delete_by_ticket(ticket):
    filename = 'orders.json'
    temp_filename = 'temp_orders.json'

    with open(filename, 'r') as file:
        try:
            orders = [json.loads(line) for line in file]
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {str(e)}")
            return

    filtered_orders = [order for order in orders if order['ticket'] == ticket]

    if not filtered_orders:
        print(f"Tidak ada order dengan ticket '{ticket}' untuk dihapus.")
        return

    with open(temp_filename, 'w') as temp_file:
        for order in orders:
            if order['ticket'] != ticket:
                json.dump(order, temp_file)
                temp_file.write('\n')
    try:
        os.remove(filename)
        os.rename(temp_filename, filename)
    except Exception as e:
        print(f"Failed to delete order with ticket '{ticket}': {str(e)}")
