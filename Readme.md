# Drone-Video-ROW-Extractor-Python

<a href="https://www.youtube.com/watch?v=sk0fxf8hDyk" target="_blank">
  
![Extract ROW from drone videos using python](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgiAg07GSs1o4QgniEqwrSHPgzGCiVhG0zwnIKjKGpcUoPhaL8TzqXmje2983O8ZaL4n-utjdikOQkNCMcsySb1azdj4DG2_JHKdkEGnaoPsJcDQHT3e5C8zh9hIJTA5SCgInHPNXB4i6NG9wCM20coltrl0ekcBio92uBLnIWtsEcMtuf2RMiZQbuE/s1600/player.PNG)
  
</a>
This python script helps in getting the coordinates for the ROW.

## How to use?

**If you are not friendly about python, you can directly open the build version from the dist folder.**

- Provide the absolute path of the video `\folders\blah\blah\wow.mp4`
- Provide the absolute path of the outpur json file. `\folder\umm\something\itWorks.json` make sure to add `.json` at the end.
- It will show you theenter code here first frame of the video. With left click create the bounding box around left line. and with right click create the bounding box around the right line. as shown below, (make sure to add at least 4 points on each side)
- ![enter image description here](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgGSvqYzb8JD3pTabd9pzHmfbXRC5TiQ48du7MNDWj03Zey4k4kiPIkOnn_fsfUEggQrIlpuOa-cJT8G3WBBzYedRAT2MMJOTmgYwTlP8hHVFRzo0w5iUWtoROySTVBx9CbEXi-pHGNuDWFYPqKhpcHbASXogdwlw9s0Ors_USMqp1ztDwKrZ62Fxbu/s400/step2.PNG)
- If you made a error dont worry hold `u` key to update them, and hold `r` key to remove them.
- To close the app simply hold `w` key.

## What after JSON?

Now we have to convert this json to line shape that AE can understand. To do that,

- Open After Effects and click the file menu > scripts > install scripts file
- Select the "ROW Plotter v1.jsx" file provided
- Click on the Window menu and select "Row Plotter v1" and you can dock this window wherever you want inside AE.
- Drag and drop the JSON file and respective video file. Right click on the video and create a composition.
- In the plugin "Refresh" and select the respective composition and its json file.
- Click on "Apply". It may take time depending on the system configuration and AE might freeze so make sure to save the file before making any changes.
