{
    'name': "Atherm",
    'version': '1.0',
    'depends': ['base'],
    'author': "Softappsit Solutions",
    'website' : 'http://www.softappsit.com',
    'sequence': 1,
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'depends' :['base','sale','stock','delivery','account','purchase'],
    'data': [
             'at_partner.xml',
             'at_config.xml',
             'at_sale.xml',
             'at_purchase.xml',
             'at_stock.xml',
             'at.account.xml',
        
       
    ],
     
    # data files containing optionally loaded demonstration data
    'demo': [
        
    ],
}