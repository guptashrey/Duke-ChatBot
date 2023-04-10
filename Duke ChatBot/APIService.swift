//
//  APIService.swift
//  Duke ChatBot
//
//  Created by Shrey Gupta on 4/2/23.
//

import Foundation
import Alamofire
import Combine

class BotService {
    
    let baseUrl = "http://52.203.49.131:8060/answer/"
    
    func askBot(query:String) {
        AF.request(self.baseUrl + query, method: .get, parameters: nil, encoding: URLEncoding.default, headers: nil, interceptor: nil).response {
            (responseData) in
            guard let data = responseData.data else {return}
            do {
                let answer = try JSONDecoder().decode(BotResponse.self, from: data)
                //print("answer == \(answer)")
            } catch {
                print("error")
            }
        }
    }
}

class APIService {
    
    let baseUrl = "http://52.203.49.131:8060/answer/"
    
    func sendMessage(message:String) -> AnyPublisher<OpenAICompletionsResponse, Error> {
        
        return Future { [weak self] promise in
            guard let self = self else { return }
            
            AF.request(self.baseUrl + message, method: .get, parameters: nil, encoding: URLEncoding.default, headers: nil, interceptor: nil).responseDecodable(of: OpenAICompletionsResponse.self) { response in
                switch response.result {
                case .success(let result):
                    print("success")
                    promise(.success(result))
                case .failure(let Error):
                    promise(.failure(Error))
                }
            }
        }
        .eraseToAnyPublisher()
    }
}

struct OpenAICompletionsBody: Encodable {
    let model: String
    let prompt: String
    let temperature: Float?
    let max_tokens: Int?
}

struct OpenAICompletionsResponse: Decodable {
    let id: String
    let choices: [OpenAICompetionsChoices]
}

struct OpenAICompetionsChoices: Decodable {
    let text: String
}

struct BotResponse: Decodable {
    let text: String
}


//class APIService {
//
//    let baseUrl = "https://api.openai.com/v1/"
//
//    func sendMessage(message:String) -> AnyPublisher<OpenAICompletionsResponse, Error> {
//        let header: HTTPHeaders = [
//            "Authorization": "Bearer \(Constants.openAIAPIKey)"
//        ]
//        let body = OpenAICompletionsBody(model: "text-davinci-003", prompt: message, temperature: 0.7, max_tokens: 256)
//
//        return Future { [weak self] promise in
//            guard let self = self else { return }
//
//            AF.request(self.baseUrl + "completions", method: .post, parameters: body, encoder: .json, headers: header).responseDecodable(of: OpenAICompletionsResponse.self) { response in
//                switch response.result {
//                case .success(let result):
//                    promise(.success(result))
//                case .failure(let Error):
//                    promise(.failure(Error))
//                }
//            }
//        }
//        .eraseToAnyPublisher()
//    }
//}
