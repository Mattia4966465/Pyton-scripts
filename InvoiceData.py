from CustomerData import Customer
from datetime import datetime
from csv import DictWriter
import pandas as pd

class Invoice:

    def __init__(self,control:str='',Id:int=0,sender:str='',recipient:str='',date:int=0,description:list=[],units:list=[],price:list=[],vat:list=[]):
        """ Initialite the invoice """
        # creation of needed variables for the items
        self.description = description
        self.units = units
        self.price = price
        self.vat = vat
        # control is a variable to know if this is a request to find the invoice into the database or to create a new one
        if control == '':
            # Read the invoices_database to reconise the new ID for this new invoice
            with open("C:\\Users\\bonot\\OneDrive\\Documenti\\Python Scripts\\Learning_Community\\Final_assignment\\invoices_database.csv") as f_object:
                self.df_read = pd.read_csv(f_object)
                f_object.close()
                # check if the database is empty
                if self.df_read.empty:
                    control_id = 0
                else:
                    control_id = int(self.df_read['ID'][-1:])
            self.id = control_id + 1
            # Ask the user for data obut sender and recipient
            sender = input('Please inser your company name (or address or ID)')
            recipient = input("Please inser the recipient's company name (or address or ID)")
            # Fill in relevant data. Use the Customer_Database to get the data for a known clients
            self.sender = Customer(sender)
            self.recipient = Customer(recipient)
            # control if the sender and the recipier are correctly been inserted
            if sender[0] != '' and recipient[0] != '':
                # control if recipier and sender are the same, if no ask to reinsert the recipient
                while self.recipient.Id == self.sender.Id:
                    recipient = input("Please inser the a different recipient's company name (or address or ID)")
                    self.recipient = Customer(recipient)
            else:
                print('Sorry, something gone wrong. Please try again!')
            # ask the client about the items of the invoice
            q = 'Yes'
            while q == 'Yes':
                self.description.append(input('Please descript the item'))
                self.units.append(int(input('Please enter the ammount per this item')))
                self.price.append(int(input('Please enter the price of the item (in €)')))
                self.vat.append(int(input('Please enter VAT fot this item (in %)')))
                q = input('Do you need to add other items? (Yes/No)')

            # write the new invoice into the database
            headersCSV = ['Invoice ID','Sender ID', 'Recipient ID', 'Date & time', 'Description','Units','Price','VAT']
            date = self.date_time()
            with open("C:\\Users\\bonot\\OneDrive\\Documenti\\Python Scripts\\Learning_Community\\Final_assignment\\invoices_database.csv", 'a', newline='') as f_object:
                # use a different row in the database for the different items
                for i in range(len(self.units)):
                    new_row = {'Invoice ID': self.id, 'Sender ID': self.sender.Id, 'Recipient ID': self.recipient.Id,
                                'Date & time': date, 'Description': self.description[i], 'Units': self.units[i],
                                'Price': self.price[i], 'VAT': self.vat[i]
                                }
                    dictwriter_object = DictWriter(f_object, fieldnames=headersCSV)
                    dictwriter_object.writerow(new_row)
                f_object.close()

        # If is a request to find the invoice use the given ID
        else:
            self.id = int(Id)
            self.sender = Customer(sender)
            self.recipient = Customer(recipient)


    def date_time(self):
        """ Recorde the date and the time of the invoice """
        date_time = datetime.now().strftime("%b-%d-%Y " + ' %M:%S:%f')[:-4]
        return date_time


    def __str__(self):
        """ Print the invoice in the correct way """
        sender = 'From:\n{0} \n{1} \n{2} \n'.format(self.sender.name, self.sender.address, self.sender.Id)
        concerning = '\nConcerning: Invoice\n'
        date = '\nInvoice ID: {0} \nInvoice date & time: {1}\n'.format(self.id, self.date_time())
        to = '\nTo:\n{0} \n{1} \n'.format(self.recipient.name, self.recipient.address)
        items = '\n'
        items_format = '{:20}| {:8}| {:8}| {:9}| {:6}%| {:7}| {:8}\n'
        items += items_format.format('Description', 'Units', 'Price', 'ex VAT', 'VAT', 'VAT', 'Total')
        ex_vat_list = []
        vat_list  = []
        total_list = []
        for i in range(len(self.description)):
            ex_vat = float(self.units[i])*float(self.price[i])
            tot_vat = ex_vat*float(self.vat[i])/100
            total = ex_vat - tot_vat
            item_string = items_format.format(self.description[i], self.units[i], self.price[i],
                                            ex_vat, self.vat[i], tot_vat, total)
            items += item_string
            ex_vat_list.append(ex_vat)
            vat_list.append(tot_vat)
            total_list.append(total)
        totals = '\nTotals: \n'
        totals += 'Total excluding VAT: {0} €\n'.format (sum(ex_vat_list))
        totals += 'Total VAT: {0} €\n'.format(sum(vat_list))
        totals += 'Total: {0} €\n'.format(sum(total_list))

        string = sender + concerning + date + to + items + totals
        return string



if __name__ == '__main__':
    a = Invoice()
    print(a)
    string(a.sender)
    #b = a.df_read['ID'][-1:] +1
    #b



    #Giorgio Roma
