import project_constant
import logging
import socketserver
import json

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        """It is a function defined in socketserver.BaseRequestHandler

        To handle incoming socket package and response respective information
        in json format.

        Returns:
            results in json format.
            because socket is a byte stream, so the we use result.encode() to 
            convert.

        """
                
        # self.request is the TCP socket connected to the client
        req = self.request.recv(1024).strip().decode()        
        req_dict = json.loads(req)
        logging.debug(req_dict)

        if req_dict['action']=='unlock' :
            result = self.action_return(req_dict)
        elif req_dict['action']=='return':
            result = self.action_return(req_dict)
       
        # just send back data from cloud restful api
        self.request.sendall(result.encode())

    def action_return(self,req):
        """ member function to handle return car action

        Parse the request information and call cloud api to update database
        to return the car

        Args:
            req: A dict mapping request parameters

        Returns:
            result in json format form cloud api restful interface

        """
        headers = {'Content-Type': 'application/json'}   
        
        r = requests.get(url=project_constant.ProjectConst.CLOUD_API_URL+"return_a_car", headers=headers, json = req)
        return r.content
        

    def action_unlock(self,req):
        """ member function to handle unlock car action

        Parse the request information and call cloud api to update database
        to unlock the car

        Args:
            req: A dict mapping request parameters

        Returns:
            result in json format form cloud api restful interface

        """
        headers = {'Content-Type': 'application/json'}   
        
        r = requests.get(url=project_constant.ProjectConst.CLOUD_API_URL+"unlock_a_car", headers=headers, json = req)
        return r.content



if __name__ == '__main__':
    """Main codes to start up mp_lister program

    Initialize a TCP socket server using pre-defined IP/port,
    then run server forever

    
    """

    logging.basicConfig(format='%(asctime)s,%(levelname)s<%(module)s>: %(message)s', level=logging.DEBUG)
    logging.info('starting mp_listener, interrupt the program with Ctrl-C...')
    

    with socketserver.TCPServer((project_constant.ProjectConst.ListenerIP, project_constant.ProjectConst.ListenerPort), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()