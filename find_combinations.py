import csv
import time
import sys


class Flight(object):
    def __init__(self, source, destination, departure, arrival, flight_number, price, bags_allowed, bag_price):
        self.source = source
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.flight_number = flight_number
        self.price = price
        self.bags_allowed = bags_allowed
        self.bag_price = bag_price

    def check_departure_compatibility(self, other_flight):
        return 3600 <= other_flight.departure_to_epoch() - self.arrival_to_epoch() <= 14400

    def departure_to_epoch(self):
        return self.to_epoch(self.departure)

    def arrival_to_epoch(self):
        return self.to_epoch(self.arrival)

    def to_epoch(self, my_time):
        return int(time.mktime(time.strptime(my_time, "%Y-%m-%dT%H:%M:%S")))

    def to_string_row(self):
        final_string = 'source\tdestination\tdeparture\tarrival\tflight_number\tprice\tbags_allowed\tbag_price\n'
        final_string += self.source + ' ' + self.destination + ' ' + self.departure + ' ' + self.arrival + ' ' + self.flight_number + ' ' + self.price + ' ' + self.bags_allowed + ' ' + self.bag_price + '\n'
        return final_string

    def __str__(self):
        return self.source + '->' + self.destination

    def __repr__(self):
        return self.source + '->' + self.destination

    def __eq__(self, other, *attributes):
        if attributes:
            d = float('NaN')
            return all(self.__dict__.get(a, d) == other.__dict__.get(a, d) for a in attributes)

        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(('source',self.source,
                     'destination',self.destination))


class FlightsCollection():
    def __init__(self, flight=None):
        if flight is not None:
            if isinstance(flight, dict):
                flight = Flight(flight['source'], flight['destination'], flight['departure'], flight['arrival'],
                                flight['flight_number'], flight['price'], flight['bags_allowed'], flight['bag_price'])
                self.flights = [flight]
            else:
                self.flights = [flight]
        else:
            self.flights = []

    def append_flight(self, flight):
        if isinstance(flight, dict):
            flight = Flight(flight['source'], flight['destination'], flight['departure'], flight['arrival'], flight['flight_number'], flight['price'], flight['bags_allowed'], flight['bag_price'])
        self.flights.append(flight)

    def merge_flight_collections(self, other_collection):
        self.flights = self.flights + other_collection.flights

    def __len__(self):
        return len(self.flights)

    def filter_by_source(self, source):
        return [flight for flight in self.flights if flight.source == source]

    def contains_source(self, source):
        return source in [flight.source for flight in self.flights]

    def return_last_row(self):
        return self.flights[-1]

    def get_max_bags_allowance(self):
        return min([int(flight.bags_allowed) for flight in self.flights])

    def get_flight_price(self):
        return sum([int(flight.price) for flight in self.flights])

    def get_one_bag_price(self):
        return sum([int(flight.bag_price) for flight in self.flights])

    def get_two_bag_price(self):
        return 2*sum([int(flight.bag_price) for flight in self.flights])

    def get_literal_elements(self):
        final_string = ''
        for flight in self.flights:
            final_string += ' | ' + str(flight)
        return final_string

    def get_route(self):
        route = str(self.flights[0])
        for flight in self.flights[1:]:
            route = route + '->' + flight.destination
        return route

    def __str__(self):
        final_string = '{:6} {:11} {:20} {:20} {:13} {:6} {:13} {:10}\n'\
            .format('source', 'destination', 'departure', 'arrival', 'flight_number', 'price', 'bags_allowed', 'bag_price')
        for flight in self.flights:
            final_string += '{:6} {:11} {:20} {:20} {:13} {:6} {:13} {:10}\n'\
                .format(flight.source,
                        flight.destination,
                        flight.departure,
                        flight.arrival,
                        flight.flight_number,
                        flight.price,
                        flight.bags_allowed,
                        flight.bag_price)
        return final_string


def find_combinations(flightToTest, my_collection, last_flight_row):
    returnPossibilities = FlightsCollection()
    for flight in my_collection.filter_by_source(flightToTest.destination):
        if not last_flight_row.contains_source(flight.source):
            if flightToTest.check_departure_compatibility(flight):
                returnPossibilities.append_flight(flight)
    if len(returnPossibilities) == 0:
        return ''
    return returnPossibilities


def final_clean(flight_collection):
    return len(flight_collection) == \
           len([value for key, value in {obj.__hash__(): obj for obj in flight_collection.flights}.items()])


def load_csv(internal=None):
    pool = FlightsCollection()
    if internal:
        stdin_input = open(internal)
    else:
        stdin_input = sys.stdin

    if not stdin_input:
        sys.stderr.write("[Error] No CSV data has been provided!\n")
        exit(1)

    try:
        with stdin_input as csv_file:
            csv_input = csv.DictReader(csv_file)
            next(csv_input, None)
            for row in csv_input:
                pool.append_flight(dict(row))
    except:
        sys.stderr.write('Error read data')
        return 1
    finally:
        stdin_input.close()
        return pool


if __name__ == "__main__":
    initialPool = load_csv() # 'input.csv'
    possibleCombinations = []

    try:
        for flight in initialPool.flights:
            possibleCombinations.append(FlightsCollection(flight))

        for my_collection in possibleCombinations:
            flightToTest = my_collection.return_last_row()

            currentCombination = FlightsCollection()
            currentCombination.append_flight(flightToTest)

            flightsToAdd = find_combinations(flightToTest, initialPool, currentCombination)

            if flightsToAdd is not '':
                currentCombination.merge_flight_collections(flightsToAdd)

                for added_flights in flightsToAdd.flights:
                    newCombination = FlightsCollection()
                    newCombination.merge_flight_collections(my_collection)
                    newCombination.append_flight(added_flights)
                    if final_clean(newCombination):
                        possibleCombinations.append(newCombination)
    except:
        sys.stderr.write('Error while manipulating flights')

    try:
        noBags = [flight_collection for flight_collection in possibleCombinations]

        print('===  No bags ===')
        for flight_collection in noBags:
            print('Route: {} Total price: {}'.format(
                flight_collection.get_route(),
                flight_collection.get_flight_price()))
            print(flight_collection)

        oneBag = [flight_collection for flight_collection in possibleCombinations
                  if flight_collection.get_max_bags_allowance() >= 1]

        print('=== One bag ===')
        for flight_collection in oneBag:
            print('Route: {} | Flight price: {} | Bag price: {} | Total price: {}'.format(
                flight_collection.get_route(),
                flight_collection.get_flight_price(),
                flight_collection.get_one_bag_price(),
                flight_collection.get_flight_price() + flight_collection.get_one_bag_price()))
            print(flight_collection)

        twoBag = [flight_collection for flight_collection in possibleCombinations
                  if flight_collection.get_max_bags_allowance() >= 2]

        print('=== Two bags ===')
        for flight_collection in twoBag:
            print('Route: {} | Flight price: {} | Bag price: {} | Total price: {}'.format(
                flight_collection.get_route(),
                flight_collection.get_flight_price(),
                flight_collection.get_two_bag_price(),
                flight_collection.get_flight_price() + flight_collection.get_two_bag_price()))
            print(flight_collection)

        print('Total flights no bags: {}\nTotal flights one bag: {}\nTotal flights two bags: {}'.format(
            len(noBags), len(oneBag), len(twoBag)
        ))
    except:
        sys.stderr.write('Error representing flights')