from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import mysql.connector

app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="test"
)

@app.route('/whatsapp', methods=['POST'])
def reply(current_chickens=None):
    incoming_msg = request.values.get('Body', '').lower()
    icm_msg = request.values.get('Body','').lower()
    last_msg = request.values.get('Body','').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if icm_msg == 'hi':
        msg.body("Please enter username and password in this format username ###### password ######")
    elif 'username' in incoming_msg and 'password' in incoming_msg:
        # extract username and password from incoming message
        username = incoming_msg.split('username')[1].split('password')[0].strip()
        password = incoming_msg.split('password')[1].strip()
        # check if username and password are valid
        cursor = mydb.cursor()
        query = "SELECT * FROM `user` WHERE `username` = %s AND `password` = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        if result:
            # if valid, send welcome message and ask for data
            resp = MessagingResponse()
            resp.message("Welcome! Please enter all the values separated by a comma in the following format: current_chickens,day_mortality,night_mortality,sale,TargetWeight,AverageDailyGainTarget,ActualWeight,AverageDailyGain,food_used,charcoal_used,vaccination_used")
            return str(resp)
        else:
            # if invalid, send error message and ask for credentials again
            resp = MessagingResponse()
            resp.message("Invalid credentials. Please enter your username and password.")
            return str(resp)
    else:
        # check if data is in the expected format
        data = incoming_msg.split(',')
        if len(data) != 11:
            resp = MessagingResponse()
            resp.message("Invalid format. Please enter all the values separated by a comma in the following format: current_chickens,day_mortality,night_mortality,sale,TargetWeight,AverageDailyGainTarget,ActualWeight,AverageDailyGain,food_used,charcoal_used,vaccination_used")
            return str(resp)
        try:
            current_chickens = int(data[0])
            day_mortality = int(data[1])
            night_mortality = int(data[2])
            sale = int(data[3])
            target_weight = float(data[4])
            average_daily_gain_target = float(data[5])
            actual_weight = float(data[6])
            average_daily_gain = float(data[7])
            food_used = float(data[8])
            charcoal_used = float(data[9])
            vaccination_used = float(data[10])
        except ValueError:
            # if any of the values cannot be converted to the expected data type, send an error message
            resp = MessagingResponse()
            resp.message("Invalid format. Please enter all values as integers or floats.")
            return str(resp)

        # do the necessary calculations and insert the data into the database
        total_mortality = day_mortality + night_mortality
        cumulative_mortality = total_mortality
        cumulative_mortality_frequency = cumulative_mortality / current_chickens * 100
        chickens_left = current_chickens - (total_mortality + sale)

        cursor = mydb.cursor()
        query = "INSERT INTO `dailyperformance` (`current_chickens`, `day_mortality`, `night_mortality`, `total_mortality`, `cumulative_mortality`, `cumulative_mortality_frequency`, `sale`, `target_weight`, `average_daily_gain_target`, `actual_weight`, `average_daily_gain`, `chickens_left`, `food_used`, `charcoal_used`, `vaccination_used`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (current_chickens, day_mortality, night_mortality, total_mortality, cumulative_mortality, cumulative_mortality_frequency, sale, target_weight, average_daily_gain_target, actual_weight, average_daily_gain, chickens_left, food_used, charcoal_used, vaccination_used)
        cursor.execute(query, values)
        mydb.commit()

        # send a confirmation message to the user
        if total_mortality > 10:
             msg="Your total mortality is too high, standard is 10. Data has been saved. Thank you!Current chickens: {result[0]}, Day mortality: {result[1]}, Night mortality: {result[2]}, Total mortality: {result[3]}, Cumulative mortality: {result[4]}, Cumulative mortality frequency: {result[5]}%, Sale: {result[6]}, Average Daily Gain: {result[7]}, Target weight: {result[8]}, Average daily gain target: {result[9]}, Actual weight: {result[10]}, Chickens Left: {result[11]}, Food used: {result[12]}, Charcoal used: {result[13]}, Vaccination used: {result[14]}."
             resp = MessagingResponse()
             resp.message(msg.format(result=values))
        else:
            success_msg = "Data has been saved. Thank you!Current chickens: {result[0]}, Day mortality: {result[1]}, Night mortality: {result[2]}, Total mortality: {result[3]}, Cumulative mortality: {result[4]}, Cumulative mortality frequency: {result[5]}%, Sale: {result[6]}, Average Daily Gain: {result[7]}, Target weight: {result[8]}, Average daily gain target: {result[9]}, Actual weight: {result[10]}, Chickens Left: {result[11]}, Food used: {result[12]}, Charcoal used: {result[13]}, Vaccination used: {result[14]}."
            resp = MessagingResponse()
            resp.message(success_msg.format(result=values))
            return str(resp)



    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)