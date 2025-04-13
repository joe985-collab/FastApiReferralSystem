import smtplib

server = smtplib.SMTP("smtp.mail.yahoo.com", 587) 
server.starttls()  
server.login("joe985testyh@yahoo.com", "WF^3iLqMJ6J!2R.")
server.quit()

print("Yahoo SMTP connection successful!")
