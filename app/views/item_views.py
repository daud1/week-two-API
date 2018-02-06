"""
ShoppingList Item Routes and View-Functions
"""
# from flasgger import swag_from
from flask import jsonify, request

from app import app
from app.forms import NewItemForm
from app.models import db, Item
from app.views.auth_views import requires_auth


# @swag_from('/swagger_docs/item/view_list_items.yml')
@app.route('/shoppinglists/<id>', methods=['GET'])
@requires_auth
def view_list(id):
    """Displays all the items belonging to a given ShoppingList."""
    if request.args.get('q'):
        list_items = Item.search(
            request.args.get("q"), id, request.args.get("page"))
        if list_items['items']:
            response = jsonify([obj.serialize for obj in list_items['items']])
            response.status_code = 200
            return response
        else:
            response = jsonify({'ERR':'List item not found.:('})
            response.status_code = 404
            return response
    else:
        list_items = Item.query.filter_by(list_id=id).all()
        items = [obj.serialize for obj in list_items]
        if len(items) != 0:
            response = jsonify(items)
            response.status_code = 200
        else:
            response = jsonify({'ERR': 'No List Items found.'})
            response.status_code = 404
    return response

# @swag_from('/swagger_docs/item/create_new_list_item.yml')
@app.route('/shoppinglists/<id>/items/', methods=['POST'])
@requires_auth
def add_item(id):
    """Adds an item to a given ShoppingList."""
    form = NewItemForm()
    if form.validate_on_submit():
        if form.quantity.data is not None:
            new_item = Item(form.name.data, id, form.quantity.data)
        else:
            new_item = Item(form.name.data, id)
        # consider using exceptions, increasing qunatity for duplicate items
        db.session.add(new_item)
        db.session.commit()
        response = jsonify({'MSG': 'Item added to list'})
        response.status_code = 201
    else:
        response = jsonify({'ERR': form.errors})
        response.status_code = 422
    return response

# @swag_from('/swagger_docs/item/edit_list_items.yml')
@app.route('/shoppinglists/<id>/items/<item_id>', methods=['PUT'])
@requires_auth
def edit_item(id, item_id):
    """Edits an item on a given ShoppingList to the string passed."""
    form = NewItemForm()

    if form.validate_on_submit():
        ed_item = Item.query.filter_by(list_id=id, item_id=item_id).first()
        if ed_item is not None:
            if form.name.data:
                ed_item.name = form.name.data

            if form.quantity.data:
                ed_item.quantity = form.quantity.data

            if form.quantity.data and form.name.data:
                ed_item.name = form.name.data
                ed_item.quantity = form.quantity.data
                db.session.commit()
        else:
            response = jsonify({'ERR': 'Item does not exist.'})
            response.status_code = 404
            return response

        response = jsonify({'MSG': 'Edited item.'})
        response.status_code = 201
    else:
        response = jsonify({'MSG': form.errors})
        response.status_code = 422
    return response

# @swag_from('/swagger_docs/item/delete_list_items.yml')
@app.route('/shoppinglists/<id>/items/<item_id>', methods=['DELETE'])
@requires_auth
def delete_item(id, item_id):
    """Deletes item from given ShoppingList."""
    del_item = Item.query.filter_by(list_id=id, item_id=item_id).first()
    if del_item:
        db.session.delete(del_item)
        db.session.commit()
        response = jsonify({'MSG': 'Successfully deleted.'})
        response.status_code = 200
    else:
        response = jsonify({'ERR': 'Requested item was not found.'})
        response.status_code = 404
    return response