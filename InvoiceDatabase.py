from InvoiceData import Invoice
import pandas as pd

class Invoices_Database:

    def __init__(self):
        """" Inizialize  the class reading the invoices_database.csv into a pandas dataframe """
        with open("C:\\Users\\bonot\\OneDrive\\Documenti\\Python Scripts\\Learning_Community\\Final_assignment\\invoices_database.csv") as f_object:
            self.df_read = pd.read_csv(f_object)


    def find_invoice(self, id_invoice:int):
        """ Find a specific invoice knowing the ID """
        control = ''
        description = []
        units = []
        price = []
        vat = []
        for i in range(len(self.df_read)):
            if self.df_read.loc[i]['ID'] == id_invoice:
                control = 'si'
                Id = self.df_read.loc[i][0]
                sender = self.df_read.loc[i][1]
                recipient = self.df_read.loc[i][2]
                data = self.df_read.loc[i][3]
                description.append(self.df_read.loc[i][4])
                units.append(float(self.df_read.loc[i][5]))
                price.append(float(self.df_read.loc[i][6]))
                vat.append(float(self.df_read.loc[i][7]))

        if control == 'si':
            string = Invoice(control,Id,sender,recipient,data,description,units,price,vat)
        else:
            string = 'The searched invoice does not exist, please enter a different ID'
        return print(string)

    def __str__(self):
        """ Print the whole Database """
        message = 'The whole database of the invoices is to big to be easy readable.\nUse the function .find_invoice() to find a specific invoice\n'
        database = '\n{0}'.format(self.df_read)
        string = message + database
        return string


if __name__ == '__main__':
    a = Invoices_Database()
    print(a)
    a.find_invoice(3)


    a.df_read.loc[3][1]
