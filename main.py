import json


class Drone_detector:
  def __init__(self):
        self.out_file = "./detection_result.mp4"
        self.url = "/Users/luther/Desktop/pythonProject/dronesample.mp4"
        self.camera_ip = "24.48.0.1"
        self.stream = None
        self.drone_identified = False


  """
  The Function below performs the frame by frame parsing for video stream.
  """
  def __call__(self, model):
      self.stream = cv2.VideoCapture(self.url) # Open the local video file directly.
      print(detector.url)

      assert self.stream != None # Make sure that there is a stream.
      #Below code creates a new video writer object to write our
      #output stream.
      x_shape = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
      y_shape = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
      four_cc = cv2.VideoWriter_fourcc(*"MJPG") #Using MJPEG codex
      out = cv2.VideoWriter(self.out_file, four_cc, 20, (x_shape, y_shape))
      ret, frame = self.stream.read() # Read the first frame.
      while ret: # Run until stream is out of frames
          start_time = time.time() # We would like to measure the FPS.
          results = self.score_frame(frame, model) # Score the Frame
          frame = self.plot_boxes(results, frame) # Plot the boxes.
          end_time = time.time()
          fps = 1/np.round(end_time - start_time, 3) #Measure the FPS.
          print(f"Frames Per Second : {fps}", f"frame is: {frame}")
          out.write(frame) # Write the frame onto the output.
          ret, frame = self.stream.read() # Read next frame.
      print(f"outfile{out}")

  def emailSubscriber(self, lat, lon):
      if self.drone_identified:
          # Email configuration
          sender_email = "your_email@example.com"
          receiver_email = "subscriber_email@example.com"
          smtp_server = "smtp.example.com"
          smtp_port = 587
          smtp_username = "your_smtp_username"
          smtp_password = "your_smtp_password"

          # Create a MIME message
          msg = MIMEMultipart()
          msg["From"] = sender_email
          msg["To"] = receiver_email
          msg["Subject"] = "Drone Alert: Seek Shelter"

          # Email content
          body = f"Dear Subscriber,\n\nA drone has been detected flying in a no-fly zone near your location ({lat}, {lon}). Please seek shelter immediately.\n\nSincerely,\nDrone Detector"

          # Attach the email content
          msg.attach(MIMEText(body, "plain"))

          # Send the email
          try:
              server = smtplib.SMTP(smtp_server, smtp_port)
              server.starttls()
              server.login(smtp_username, smtp_password)
              server.send_message(msg)
              server.quit()
              print("Email sent successfully!")
          except Exception as e:
              print("Failed to send email:", e)

  def check_air_advisory(self, longitude, latitude):

      # Calculate the coordinates for a square representing a mile in width around the center point
      lat_mile = 0.01449275362  # Approximately 1 mile in latitude
      lon_mile = 0.01818181818  # Approximately 1 mile in longitude at this latitude

      # Define the URL
      url = f"https://app.avision.io/B4UFLY?lat={latitude}&lng={longitude}"

      # Send a GET request to the URL
      session = HTMLSession()
      response = session.get(url)
      response.html.render()

      # Check if the request was successful
      if response.status_code == 200:
          # Parse the HTML content of the page using BeautifulSoup
          soup = BeautifulSoup(response.html.html, "html.parser")

          # Find all elements with class="advisory-type" or class="advisory-text"
          filtered_elements = soup.find_all("app-b4u-fly-advisories")
          # filtered_elements_next = soup.find_all("div", class_="ps-content")

          # Combine the filtered elements into a string
          filtered_content = "\n".join(str(element) for element in filtered_elements)

          # Print or do something with the filtered content
          print(filtered_content)
          if "Flight Restricted Airspace" in filtered_content:
              self.emailSubscriber(latitude,longitude)
      else:
          print("Failed to retrieve the page. Status code:", response.status_code)


  """
    The function below checks based on the GPS of the camera by IP address, if the airspace it's in is restricted
  """
  def check_airspace(self):
      print("checking if allowed airspace by GPS coordinates")
      if self.camera_ip:
          # Define the URL for the API
          url = f"http://ip-api.com/json/{self.camera_ip}"

          # Send a GET request to the API
          response = requests.get(url)

          # Check if the request was successful (status code 200)
          if response.status_code == 200:
              # Print the JSON response
              print(response.json())
              json_data = json.loads(response.content.decode('utf-8'))
              latitude = json_data['lat']
              longitude = json_data['lon']
              print(latitude,longitude)

              self.check_air_advisory(latitude,longitude)

          else:
              # Print an error message if the request was not successful
              print(f"Error: {response.status_code}")
          # call
      else:
          print("no camera IP address source, unable to find location")

  """
  The function below takes the results and the frame as input and plots boxes over all the objects which have a score higer than our threshold.
  """
  def plot_boxes(self, results, frame):
      labels, cord = results
      n = len(labels)
      x_shape, y_shape = frame.shape[1], frame.shape[0]
      for i in range(n):
          row = cord[i]
          # If score is less than 0.2 we avoid making a prediction.
          if row[4] < 0.2:
              continue
          x1 = int(row[0]*x_shape)
          y1 = int(row[1]*y_shape)
          x2 = int(row[2]*x_shape)
          y2 = int(row[3]*y_shape)
          bgr = (0, 255, 0) # color of the box
          classes = model.names # Get the name of label index
          if classes[labels[i]] == "airplane":
              print(f"AIRCRAFT DETECTED {classes[labels[i]]}")

              # since each frame could mean an identified object, only check airspace if a drone has not already been identified
              if not self.drone_identified:
                self.check_airspace()
          label_font = cv2.FONT_HERSHEY_SIMPLEX #Font for the label.
          cv2.rectangle(frame, \
                        (x1, y1), (x2, y2), \
                        bgr, 2) #Plot the boxes
          cv2.putText(frame,\
                      classes[labels[i]], \
                      (x1, y1), \
                      label_font, 0.9, bgr, 2) #Put a label over box.
          return frame


  """
  The function below identifies the device which is available to make the prediction and uses it to load and infer the frame. Once it has results it will extract the labels and cordinates(Along with scores) for each object detected in the frame.
  """

  def score_frame(self, frame, model):
      device = 'cuda' if torch.cuda.is_available() else 'cpu'
      #model = torch.from_numpy(model)
      model.to(device)

      results = model(frame)
      labels = results.xyxyn[0][:, -1].numpy()
      cord = results.xyxyn[0][:, :-1].numpy()
      return labels, cord



if __name__ == '__main__':
    import cv2
    import numpy as np
    import torch
    from torch import hub
    import time
    import requests
    from bs4 import BeautifulSoup
    from requests_html import HTMLSession
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    model = torch.hub.load('ultralytics/yolov5','yolov5s',pretrained=True)
    detector = Drone_detector()
    detector.__call__(model)
    print('PyCharm')

