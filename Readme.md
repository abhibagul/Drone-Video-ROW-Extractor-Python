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
- Click on the Window menu and select "Row Plotter v1" and you can dock this window wherever you want inside AE. <img alt="" border="0" data-original-height="416" data-original-width="606" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj1Xgr_S-dq3oRKRRpOGFNngcK7hj-WPgq0PV9M0ZxNlSuz2aGW9CUuXjahUR2A2PdAJ8D_Ob-_aNoQyaiNNDXYSVIJxIJijMhz_3Gev8TSiWo_w0yb-8aaqsNsFcM-cIeRTKP0e3qtvmoFDdKg4zpXucKCvEy4hhM9DmL0Kys9SitCxo3m3g68_aq-xDVe/s1600/aeplugin.JPG"/>
- Drag and drop the JSON file and respective video file. Right click on the video and create a composition.
- In the plugin "Refresh" and select the respective composition and its json file.
  <img alt="" border="0" data-original-height="998" data-original-width="1040" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj2dE3ZKszWxVP2k5rtFdqZSOxwz06udBLytZ_ph2uL6LvNwNEn7u1Q_xa_l40gEyEIiMNFPsKPHlUeQBllW61hZhYCn24S_oYF-PtZ7OCpKC5uKvPudnkSxITDedScJZ2rfaa8kvQ2uD0O7qaiTxLIUP-AkSNfb7uJsn7r8S1JrBBgXxBBL2EwTJYhCq1i/s1600/aeplug2.JPG"/>
- Click on "Apply". It may take time depending on the system configuration and AE might freeze so make sure to save the file before making any changes.
      <img alt="" border="0" data-original-height="994" data-original-width="1033" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjsKSAE2YCjOTg2WVuU6Ggbue3PGgxVvDhaMwJ5zRkkAep_dE1o8jDloa2BqLU1ZBZdOBakhqnGvxUM0CLeg3BejLTob-YPYLYtNF2PCcmF3X8coUrGZy2svaK-SEwW7fPbGxpN6O5hpBvKREfCYOuD6jvuomFr_yJl6mJWd3R0d3o70Om5bUvfPW24wJfW/s1600/aeplugin3.JPG"/>
