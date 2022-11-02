from CustomerDatabase import Customer_Database
from CustomerData import Customer
from InvoiceData import Invoice
from InvoiceDatabase import Invoices_Database

# reading the csv file
customer_database = Customer_Database()
invoices_database = Invoices_Database()

######################
# Create a new invoice
######################
# new_invoice = Invoice()
# print(new_invoice)

##########################
# Find an existing customer
# to find an existing customer and his history in the database, first print the whole
# database and check the name of the company (or the full name of a person).
# Then inser the name in the Customer() class.
# If the name doesn't exist in the database, the code will ask for other relevant data
# and will add them.
##########################
# print(customer_database)
# customer = Customer('Mattia Rossi')
# print(customer)


##########################################
# Find a specific invoice in the database
# to find a specific invoice in the database
# first print the whole database and check the invoice ID.
# Then inser the ID in the .find_invoice() function
#########################################
# print(invoices_database)
# existing_invoice = invoices_database.find_invoice(11)
