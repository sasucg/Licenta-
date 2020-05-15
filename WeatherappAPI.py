from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import requests
import json

root = Tk()
root.title("Create new window")
root.iconbitmap('C:/Users/lenovo/PycharmProjects/LicentaSasu/Icon.ico')
root.geometry("800x40")

#http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=89129&distance=5&API_KEY=7672E1FE-D9FB-40BE-B051-65ECBAA370E7



try:
    api_request = requests.get("http://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=94506&distance=5&API_KEY=7672E1FE-D9FB-40BE-B051-65ECBAA370E7")
    api = json.loads(api_request.content)

    city = api[0]['ReportingArea']
    quality = str(api[0]["AQI"])
    category = api[0]["Category"]["Name"]

    if category == "Good":
        weather_color = "green"
    elif category == "Moderate":
        weather_color = "yellow"
    elif category == "Unhealthy for Sensitive Groups":
        weather_color = "blue"
    elif category == "Unhealthy":
        weather_color = "purple"
    elif category == "Very Unhealthy":
        weather_color = "red"
    elif category == "Hazardous":
        weather_color = "grey"

    root.configure(background=weather_color)
    myLabel = Label(root, text="Vremea in " + city + " este " + category + " avand calitatea aerului de " + quality, font=("Helvetica",20), background=weather_color, )
    myLabel.pack()
except Exception as e:
    api = "Api Error...."
    myLabel = Label(root, text=api)
    myLabel.pack()



root.mainloop()

