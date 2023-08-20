from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Text

def create_table():
    
   meta = MetaData()

   pdf_data = Table(
      'pdf_data', meta, 
      Column('id', Integer, primary_key = True), 
      Column('file_name', String, unique=True), 
      Column('Subject',Text),
      Column('Trapped',Text),
      Column('Creator',Text),
      Column('extracted_text', Text), 
      Column('Author', Text),
      Column('CreationDate', Text),
      Column('Producer', Text),
      Column('Title', Text),
      Column('ModDate',Text),
      Column('Keywords', Text)  # Add this line
   )
   engine = create_engine('sqlite:///pdf_data.db', echo = True)

   meta.create_all(engine)


if __name__ == "__main__":
   create_table()
