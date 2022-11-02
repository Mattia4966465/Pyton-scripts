import pandas as pd
import csv
from CustomerDatabase import Customer_Database

class Customer(Customer_Database):

    def __init__(self, name):
        super().__init__()
        """ Find a specific client from the customer_database to initialise the class """
        self.customer = self.find_client(name)[0]
        # check if the client has been found
        if self.customer != []:
            self.Id = self.customer[0]
            self.name = self.customer[1]
            self.address = self.customer[2]

    def customer_history(self):
        """" Find all the invoices for this customer (incoming and outgoing) """
        # Read the invoices database
        with open("C:\\Users\\bonot\\OneDrive\\Documenti\\Python Scripts\\Learning_Community\\Final_assignment\\invoices_database.csv") as f_object:
            invoices_database = pd.read_csv(f_object)
        list = []
        id_list = []
        counter = 0

        for i in range(len(invoices_database)):
            sender = invoices_database.loc[i][1]
            recipient = invoices_database.loc[i][2]
            if recipient == self.Id  or sender == self.Id:
                counter +=1
                list.append(invoices_database.loc[i])
                id_list.append(invoices_database.loc[i][0])

        if list != []:
            df = pd.DataFrame(list, index=id_list)
        else:
            df = 'This customer has not yet sent or received an invoice'

        return df



    def __str__(self):
        """ Print the relevant info about the customer """
        if self.customer != []:
            customer = ' ID:      {0}\n Name:    {1}\n Address: {2}\n'.format(self.Id, self.name, self.address)
            history = '\n{0}'.format(self.customer_history())
            string = customer + history
        else:
            string = ''
        return string



if __name__ == '__main__':
    a = Customer('Mattia Rossi')
    print(a)

    #a.customer_history()

    # a.add_customer('Areo Cairoli', '9754RG Groningen')
    # a.add_customer('Tepi Ciucia', '9711RF Groningen')
