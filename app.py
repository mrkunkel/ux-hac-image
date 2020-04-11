import os
import sys
import requests
from io import BytesIO
from requests.exceptions import HTTPError
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def return_image():

    # Get Home Assitant url
    hac_url = os.environ.get('HAC_URL')

    # Get current states from Home Assistant Core
    with open("hac.dw",'rb') as hac_payload:
        try:
            hac_headers = {'content-type': 'text/plain'}
            response = requests.post(hac_url, data=hac_payload, verify=False, headers=hac_headers)
            response.raise_for_status()
            hac_states = response.json()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

    state_weather = ""
    states_lights = ""
    states_phones = ""
    states_devices = ""
    weather_icon = ""
    weather_font = ImageFont.truetype('fonts/meteocons-webfont.ttf', 45)

    eInkImg = Image.new("1", (640,384), 1)
    draw = ImageDraw.Draw(eInkImg)

    # Draw boxes
    draw.line(((8,100), (eInkImg.size[0]-8,100)), fill=0, width=2)
    draw.line(((eInkImg.size[0]/2,8), (eInkImg.size[0]/2,100)), fill=0, width=2)

    # Say Hello
    draw.multiline_text((16,50), "Hello Krista and Camden!", fill=0, font=None, align="left")

    for state in hac_states:
      if state["group"] == "weather":
        state_weather = "It is " + state["state"] + " in the " + state["name"] + "\nThe temperature is " + str(int(state["temperature"])) + " F\nThe humidity is " + str(state["humidity"]) + " %"
        if state["state"] == "lightning-rainy":
          weather_icon = "Z"
        elif state["state"] == "windy-variant":
          weather_icon = "F"
        elif state["state"] == "partlycloudy":
          weather_icon = "H"
        elif state["state"] == "exceptional":
          weather_icon = "B"
        elif state["state"] == "clear-night":
          weather_icon = "C"
        elif state["state"] == "snowy-rainy":
          weather_icon = "X"
        elif state["state"] == "lightning":
          weather_icon = "P"
        elif state["state"] == "pouring":
          weather_icon = "R"
        elif state["state"] == "cloudy":
          weather_icon = "Y"
        elif state["state"] == "rainy":
          weather_icon = "R"
        elif state["state"] == "snowy":
          weather_icon = "W"
        elif state["state"] == "sunny":
          weather_icon = "B"
        elif state["state"] == "windy":
          weather_icon = "F"
        elif state["state"] == "hail":
          weather_icon = "X"
        elif state["state"] == "fog":
          weather_icon = "M"
      elif state["group"] == "light":
        states_lights += state["name"] + " : " + state["state"] + "\n"
      elif state["group"] == "phone":
        states_phones += state["name"] + " - " + state["state"] + "(" + str(state["battery_level"]) + ")\n"
      elif state["group"] == "devices":
        states_devices += state["name"] + " : " + state["state"] + "\n"

    # Weather Icon
    weather_font_width, weather_font_height = weather_font.getsize(weather_icon)
    draw.text((eInkImg.size[0]/2+(weather_font_width/2),58-(weather_font_height/2)),weather_icon, font=weather_font, fill=0)

    # Weather
    draw.multiline_text(((eInkImg.size[0]/2)+weather_font_width+48,58-(weather_font_height/2)), state_weather, fill=0, font=None, align="right")

    # Phone states
    draw.multiline_text((400,116), states_phones, fill=0, font=None, align="right")

    # Light states
    draw.multiline_text((16,116), states_lights, fill=0, font=None, align="right")

    # Device states
    draw.multiline_text((16,216), states_devices, fill=0, font=None, align="left")

    del draw

    # Create in-memory image to return
    eii_io = BytesIO()
    eInkImg.save(eii_io, 'PNG')
    eii_io.seek(0)
    return send_file(eii_io, mimetype='image/png')

if __name__ == "__main__":
   app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
