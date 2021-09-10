from datetime import datetime
from logging import error
from flask import Flask, request, jsonify
from heapq import heappush, heappop
from http import HTTPStatus

_app = Flask(__name__)


class Payer:
    """representation of a Payer"""

    def __init__(self, name, points=0):
        """each Payer contains a name and associated points"""
        self.name = name
        self.points = points

    def update(self, delta):
        """update points for this Payer"""
        self.points += delta

    def __lt__(self, other):
        if self.name == other.name:
            return self.points < other.points
        return self.name < other.name

    def __le__(self, other):
        if self.name == other.name:
            return self.points <= other.points
        return self.name <= other.name
    
    def __str__(self):
        """JSON string of a Payer"""
        return "{ %s : %d }" % (self.name, self.points)

    def __repr__(self):
        """for debugging purposes"""
        return self.__str__()

class Transaction:
    """representation of a Transaction"""

    def __init__(self, payer, timestamp):
        """Each transaction contains a Payer with name and points and the timestamp"""
        self.payer = payer
        self.timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    def __str__(self):
        return {"payer": str(self.payer), "timestamp": self.timestamp}


class Collection:
    def add():
        pass

class Payers(Collection):
    """collection (database) of Payers"""

    def __init__(self):
        """collection includes the Payers and balances in separate dicts"""
        super().__init__()
        self.payers = dict()    # K: name, V: Payer
        self.balances = dict()  # K: name, V: points

    def add(self, payer):
        """add a new payer into this collection, if already exists
        then update the points to existing payer"""
        name = payer.name
        points = payer.points

        if name in self.payers:
            self.payers[name].update(points)
        else:
            self.payers[name] = payer

        self._update_balance(name)

    def get_payer(self, name):
        """fetch payer based on name"""
        if name in self.payers:
            return self.payers[name]
        return None

    def update_payer(self, name, points):
        """update payer points externally"""
        if name in self.payers:
            self.payers[name].update(points)
            self._update_balance(name)

    def get_balances(self):
        """get collection of balances"""
        return self.balances

    def _update_balance(self, name):
        """update balance dict with points from payers dict"""
        self.balances[name] = self.payers[name].points

class Transactions(Collection):
    """collection (database) of Transactions"""

    def __init__(self):
        """collection is a priority queue of Transactions with
        the minimum (old) transaction is based on the timestamp"""
        super().__init__()
        self.transactions = []

    def is_empty(self):
        """is the queue empty?"""
        return not self.transactions

    def add(self, tn):
        """push a new transaction into the priority queue"""
        heappush(self.transactions, (tn.timestamp, tn.payer))
    
    def peek(self):
        """get what is at the top of the queue"""
        if not self.is_empty():
            return self.transactions[0][1]
        return None

    def pop(self):
        """remove the old transaction from the queue"""
        if not self.is_empty():
            heappop(self.transactions)


class ApiHandler:
    """contains functions to make changes based on API calls"""

    def __init__(self, payers, transactions):
        """includes Payers and Transactions collections"""
        self.payers = payers
        self.transactions = transactions

    def add_transaction(self, name, points, timestamp):
        """for handling /add_transaction : add new Payer and Transaction to collections"""
        tn = Transaction(Payer(name, points), timestamp)
        payer = Payer(name, points)

        self.transactions.add(tn)
        self.payers.add(payer)

    def spend_points(self, user_points):
        """for handling /spend : updates the current payers' balances based off
        the user points"""
        deductions = {}
        
        while not self.transactions.is_empty() and user_points > 0:
            old = self.transactions.peek()
            name = old.name
            points = old.points
            delta = -points

            if user_points < points:
                delta = -user_points
                user_points = 0
                old.update(delta)
            else:
                user_points += delta
                self.transactions.pop()

            deductions[name] = deductions.get(name, 0) + delta
            self.payers.update_payer(name, delta)
            
        return deductions
            
    def get_payers_balances(self):
        """for handling /balances : get the payers' balances in one collection"""
        return self.payers.get_balances()


_handler = ApiHandler(Payers(), Transactions())

class ApiController:
    """controller for API calls, gets values from request and return back JSON messages"""

    @_app.route("/add_transaction", methods=["POST"])
    def add_transaction():
        payer = request.form.get("payer").upper()
        points = int(request.form.get("points"))
        timestamp = request.form.get("timestamp")

        _handler.add_transaction(payer, points, timestamp)
        
        return jsonify('', HTTPStatus.OK.value)

    @_app.route("/spend", methods=["POST"])
    def spend_points():
        points = int(request.form.get("points"))
        deltas = _handler.spend_points(points)

        return jsonify(deltas)

    @_app.route("/balances", methods=["GET"])
    def get_balances():
        balances = _handler.get_payers_balances()

        return jsonify(balances)

    def run(debug=False):
        """running the app"""
        _app.run(debug=debug)


if __name__ == "__main__":
    ApiController.run(True)
