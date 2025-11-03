# execute in cmd

# spec and exe
NAME = create_paintingChanger
SRC = main.py
# bundle path
BUNDLE = bundle
# icon path
ICON = bundle/icon.ico

.PHONY: exe clean

exe : 
	pyinstaller ${SRC} -F -w -n ${NAME} --add-data ${BUNDLE}:${BUNDLE} --icon ${ICON} --clean

clean :
	del ${NAME}.spec
	rmdir /s /q build\${NAME} 

#------------