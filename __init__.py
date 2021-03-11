from design_1.service import RequestServer as baker, StockInterface as manager, CalculatorCommandLineInterface as cli
def drive():
    #This would get I/P from CLI
    #We can have I/P format in any way.
    input_map = cli.get_cli_request()
    #If Needed
    #Creates a baker request Object from dict
    api_req = baker.bake(input_map)
    #Send appropriate Request
    manger.serve_request(api_req)


if __name__ == '__main__':
    drive()