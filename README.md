# MacPopups
A small set of python classes to simply create Mac popup-windows like message boxes, file dialogs, etc.


MacPopups uses `pyobjc` so `pyobjc` needs to be installed when trying to use it.
MacPopups is in development and feedback such as suggestions are highly wanted. 

## Usage


```py
alert = Alert("Title", "Description", ["Button 1", "Button 2"], check_box=True,
                  box_title="Don't show again", default=[0])
alert.set_icon("filepath/image",rounded_corners=True)
alert.buttons[0].set_color(hex="#90EE90")
selection = alert.show()
```
This code will produce something like this: 


<img width="372" alt="Bildschirmfoto 2021-12-27 um 19 29 40" src="https://user-images.githubusercontent.com/96743662/147498159-30359130-f459-4aa7-8836-92293b298b80.png">

Note that I am on Mac Os Monterey (12.0) and haven't tested the classes on other versions of Mac Os.
