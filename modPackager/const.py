

## layout and param config
# mod base info
baseInfo = { # "key": <entrysize-row>
  "id": 1, 
  "name": 1, 
  "version": 1 , 
  "description": 3,
}

# file dialog Types
fTypes = {
  "img" : [
          ("image file ", "*.png;*.PNG;*.jpg;*.jpeg;*.JPG;*.JPEG;*.webp"),
          ("png file ", "*.png;*.PNG"),
          ("jpeg file ", "*.jpg;*.jpeg;*.JPG;*.JPEG"),
          ("webp file ", "*.webp;")
        ],
  "jar" : [
          ("mod jar file ", "*.jar"),
        ]
}