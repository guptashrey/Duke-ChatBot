//
//  ContentView.swift
//  Duke ChatBot
//
//  Created by Shrey Gupta on 4/1/23.
//

import SwiftUI
import Combine

struct ContentView: View {
    @State var chatMessages: [ChatMessage] = []
    @State var messageText: String = ""
    @State var cancellables = Set<AnyCancellable>()
    
    let apiservice = APIService()
    
    var body: some View {
        VStack {
            Label("**Duke ChatBot**", image: "test")
            ScrollView {
                LazyVStack {
                    ForEach(chatMessages, id:\.id) {message in
                        messageView(message: message)
                    }
                }
            }
            HStack {
                TextField("Ask me anything", text: $messageText)
                    .padding()
                    .background(.gray.opacity(0.1))
                    .cornerRadius(12)
                Button {
                    sendMessage()
                } label: {
                    Text("Send")
                        .foregroundColor(.white)
                        .padding()
                        .background(.black)
                        .cornerRadius(12)
                }
            }
        }
        .padding ()
    }
    
    func messageView(message: ChatMessage) -> some View {
        HStack {
            if message.sender == .me { Spacer() }
            Text (message.content)
                .foregroundColor(message.sender == .me ? .white : .black)
                .padding ()
                .background (message.sender == .me ? .blue :
                        .gray.opacity(0.1))
                .cornerRadius (16)
            if message.sender == .api { Spacer() }
        }
    }
    
    func sendMessage() {
        let myMessage = ChatMessage(id: UUID().uuidString, content: messageText, dateCreated: Date(), sender: .me)
        chatMessages.append(myMessage)
        //botservice.askBot(query: messageText)
        apiservice.sendMessage(message: messageText).sink { completion in
            //Handle Error
        } receiveValue: { response in
            guard let textResponse = response.choices.first?.text.trimmingCharacters(in:
                    .whitespacesAndNewlines.union(.init(charactersIn: "\""))) else { return }
            let apiMessage = ChatMessage(id: response.id, content: textResponse, dateCreated: Date(), sender: .api)
            chatMessages.append(apiMessage)
        }
        .store(in: &cancellables)
        messageText = ""
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

struct ChatMessage {
    let id: String
    let content: String
    let dateCreated: Date
    let sender: MessageSender
}

enum MessageSender {
    case me
    case api
}
