
## Welcome to OpenNotify, this a Push Notification Server and Client Management for Your Own and Commercial use.

<details>
  <summary><strong>Setup Server</strong></summary>

 - [Import Package and Required Object](#import-package-and-required-object)
 - [Server Ip Address](#server-ip-address)
 - [Server Port](#server-port)
 - [Create Server Object](#create-server-object)
 - [Set the Message Model](#set-the-message-model)
 - [Generate Id ](#generate-id)
 - [Start the server](#start-the-server)
 - [Start The Server](#start-the-server)

</details>
</br>

<details>
  <summary><strong>Setup Client</strong></summary>

 - [Import Package and Required Object](#import-package-and-required-object)
 - [Server Ip Address](#server-ip-address)
 - [Server Port](#server-port)
 - [Create Client Object](#create-client-object)
 - [Message Receiver Function](#message-receiver-function)
 - [Set Message Model](#set-message-model)
 - [Set App Id ](#set-app-id)
 - [Set App Name ](#set-app-name)
 - [Set Id ](#set-id)
 - [Set Receiver](#set-receiver)
 - [Start The Client](#start-the-client)
 - [Send Message](#send-message)

</details>
</br>


# Server
First setup all requierd variables and objects

### Import Package and Required Object
```from OpenNotify import Server, MessageModel ```

### Custom Message model 
this model for thinks what you get and store in server
> [!Note]
> id{string) and to_id(string) is important for server to run 
```
class Message(MessageModel):

	id:str
	to_id:str
	body:str
	icon:str
```

### Server Ip address
``` ip : str = '127.0.0.1' ```
### Server Port
``` port : int = 200 ```

### Create Server Object
##### Set the parameter of ip(String), port(integer)
``` server = Server(ip, port) ```

### Set the Message Model 
##### Set the model We Created on the Start
``` server.setModel(Message) ```

### Generate Id 
>[!Note]
>If you Starting the server for first time use this method if you already run the server skip this part

``` server.generateID('OpenNotify') ```

### Start the server
``` server.start() ```

</br>

# Client
First setup all requierd variables and objects

### Import Package and Required Object
```from OpenNotify import Client, MessageModel ```

### Custom Message model 
> [!Note]
> this model will be same as the server message model
> id{string) and to_id(string) is important for sending message 
```
class Message(MessageModel):

	id:str
	to_id:str
	body:str
	icon:str
```

### Message Receiver Function
>{!Note}
>It will give the MessageModel Object as the parameter
```
load_message(message:Message) -> None:
    print(f" {message.id} -> {message.body}")
```

### Server Ip address
``` ip : str = '127.0.0.1' ```
### Server Port
``` port : int = 200 ```

### Create Client Object
##### Set the parameter of ip(String), port(integer)
``` client = Client(ip, port) ```

### Set Message Model 
##### Set the model We Created on the Start
``` client.setModel(Message) ```

### set App Id 
##### Set the App Id that we generate on the server
``` client.setAppId(self.APPID) ```

### Set App Name
##### Set the app name that we entered on the server
``` client.setAppName(self.APPNAME) ```

### Set Id 
Unique Client Id for server identify the user
``` client.setId(self.ID) ```

### Set Receiver 
#####Set message receiver function that will trigger when a message receives from server 
``` client.receiver.connect(load_message) ```

### Start the Client
>[!Note]
> If the Server is not running it will raise a ConnectionRefusedError
``` client.start() ```

### Send Message
##### Create Message Model Obejst
``` message = Message() ```

##### Set Client Id
``` message.id = self.ID ```
##### Set To Id
###### message to client id
``` message.to_id = self.TO ```

##### Set Body
###### body is the content you will send to the other client
``` message.body = "Hi bro" ```

##### Send Message Model
``` client.sendMessage(message) ```




