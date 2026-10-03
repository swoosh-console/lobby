For DragonRise controllers the following setting has to be provided to Cemu before launching the settings menu:

```
flatpak override --user --env=SDL_GAMECONTROLLERCONFIG="03000000790000000600000010010000,DragonRise Inc. Generic USB Joystick,platform:Linux,x:b3,a:b2,b:b1,y:b0,back:b8,start:b9,dpleft:h0.8,dpdown:h0.4,dpright:h0.2,dpup:h0.1,leftshoulder:b4,lefttrigger:b6,rightshoulder:b5,righttrigger:b7,leftstick:b10,rightstick:b11,leftx:a0,lefty:a1,rightx:a3,righty:a4," info.cemu.Cemu
```

This will force Cemu to translate the DragonRise controller to a compatible SDLController.