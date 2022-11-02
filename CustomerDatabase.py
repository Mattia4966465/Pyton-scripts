import pandas as pd
from random import randint
from csv import DictWriter

class Customer_Database:

    def __init__(self):
        """" Inizialize the class reading the customer_database """
        self.df = pd.read_csv("C:\\Users\\bonot\\OneDrive\\Documenti\\Python Scripts\\Learning_Community\\Final_assignment\\customer_database.csv")

    def __str__(self):
        """ Print the customer database """
        string = ''
        database_format = '{:7} {:25} {:30}\n'
        string += database_format.format('ID', 'COMPANY NAME', 'ADDRESS')
        for n in range(len(self.df)):
            customer = self.df.loc[n]
            Id = customer[0]
            name = customer[1]
            address = customer[2]
            customer_string = database_format.format(Id, name, address)
            string += customer_string
        return string


    def read_database(self):
        """ Read the uploaded database """
        # This is needed in order to not re-add the same client if the code is run two times
        Id_list = []
        name_list = []
        address_list = []

        with open("C:\\Users\\bonot\\OneDrive\\Documenti\\Python Scripts\\Learning_Community\\Final_assignment\\customer_database.csv") as f_object:
            df_read = pd.read_csv(f_object)
            Id_list = df_read['ID'].tolist()
            name_list = df_read['Company Name'].tolist()
            address_list = df_read['Address'].tolist()
        return Id_list, name_list, address_list


    def find_client(self, name, Id: str= '', address: str=''):
        """" Method to find a specic client in the database """
        # first check if the client already exist in the database, in case return its relevan data
        db_read = self.read_database()
        Id_list = db_read[0]
        name_list = db_read[1]
        address_list = db_read[2]
        string = ''
        string_b = ''

        if name.upper() in Id_list:
            string = self.df.loc[Id_list.index(name)]
        elif name in name_list:
            string = self.df.loc[name_list.index(name)]
        elif  name in address_list:
            string = self.df.loc[address_list.index(name)]
        # what happen if the customer is not in the database yet
        else:
            question = input("The customer: " + name + " is not in the database, do you want to add it? (Yes/No)")
            if question.upper() == 'YES':
                self.add_customer(name)
                string_b = "The custumer has been added to the database"

        return list(string), print(string_b)


    def add_customer(self, name: str='', address: str=''):
        """ Add a new customer to the database if needed """
        # first check if the client already exist in the database
        db_read = self.read_database()
        name_list = db_read[1]
        address_list = db_read[2]

        if name not in name_list and address not in address_list:
            # check if the name or the address of the client are already given
            if name == '':
                name = input('Please enter the company name')
            if address == '':
                address = input('Please enter the address')
            ##################
            # Here can be added the btw and the bankaccount
            #################
            # btw = input('Please enter btw-id for the company')
            # bankaccount = input('Please enter the bankaccount')

            # write the new client in the customer_database.csv, create also an ID for the client
            headersCSV = ['ID','Company Name','Address']
            new_Id = name[:3].upper() + name[-2:].upper()
            new_row = {'ID': new_Id,'Company Name': name,'Address': address}
            with open("C:\\Users\\bonot\\OneDrive\\Documenti\\Python Scripts\\Learning_Community\\Final_assignment\\customer_database.csv", 'a', newline='') as f_object:
                dictwriter_object = DictWriter(f_object, fieldnames=headersCSV)
                dictwriter_object.writerow(new_row)
                f_object.close()

            string = 'New line customer added'
        else:
            string = 'Already there'
        return print(string)



if __name__ == '__main__':
    a = Customer_Database()
    print(a)
    #a.add_customer()
    a.find_client('rocco')

    # b[1]
