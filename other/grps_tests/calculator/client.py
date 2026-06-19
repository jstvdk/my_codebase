import grpc
import calculator_pb2
import calculator_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = calculator_pb2_grpc.CalculatorStub(channel)

    request = calculator_pb2.AddRequest(num1=10, num2=20)
    response = stub.AddNumbers(request)

    print(f"Server responded: {response.result}")

if __name__ == "__main__":
    run()