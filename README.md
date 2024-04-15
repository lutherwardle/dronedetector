# Py Drone Detector
### plug in cctv or wireless camera stream application allowing drone detection 

#### users can deploy this app as a flask or django server and plugin their camera IP to detect drones, check their airspace validity, and send out messages to given email subscribers

- project can be expanded upon by using GSM modules to send out text messages for wider reaching alerts
- Keep in mind if using a proxy for any reason (firewall issues etc) , the application converts your Camera IP into GPS coordinates
- currently the best case for this application is for camera streams provided by APIs such as traffic cams or boardwalk cams, hosting this application on your local network without configuring firewall access to the desired port will NOT work
- this version is using beautiful soup as a scraper for an FAA approved map program to get the airspace restrictions within a 2 mile radius of the given coordinates... I don't take any responsibility for anyone using this service but I have added a condition to reduce calls to the app, this implementation is just intended to show a POC not commercial or even extended personal use. 
