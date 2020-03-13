from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
import sqlite3


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be null")

    @jwt_required()
    def get(self, name):
        item = self.find_by_name(name)
        if item:
            return item
        return {'message': 'Item not found'}, 404

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items WHERE name=?"
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {'item': {'name': row[0], 'price': row[1]}}

    @jwt_required()
    def post(self, name):
        if self.find_by_name(name):
            return {'message': "Item with name '{}' already exist".format(name)}

        data = Item.parser.parse_args()
        item = {'name': name, 'price': data['price']}
        try:
            self.insert_data(item)
        except:
            return {'message': 'An error occurred while inserting data..'}, 500  # Internal Server Error

        return item, 201

    @jwt_required()
    def delete(self, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "DELETE FROM items WHERE name=?"
        cursor.execute(query, (name,))

        connection.commit()
        connection.close()
        return {'message': 'Item Deleted'}

    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()

        item = self.find_by_name(name)
        updated_item = {'name': name, 'price': data['price']}

        if item is None:
            try:
                self.insert_data(updated_item)
            except:
                return {'message': 'An error occurred while inserting data..'}, 500  # Internal Server Error

        else:
            try:
                self.update_data(updated_item)
            except:
                return {'message': 'An error occurred while inserting data..'}, 500  # Internal Server Error

        return updated_item

    @classmethod
    def update_data(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "UPDATE items set price=? WHERE name=?"
        cursor.execute(query, (item['price'], item['name']))

        connection.commit()
        connection.close()

    @classmethod
    def insert_data(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(query, (item['name'], item['price']))

        connection.commit()
        connection.close()


class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM items"
        result = cursor.execute(query)
        items = []
        rows = result.fetchall()
        for row in rows:
            items.append({'name': row[0], 'price':row[1]})
        connection.close()
        return {'items': items}
