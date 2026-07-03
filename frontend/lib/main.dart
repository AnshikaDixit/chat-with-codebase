import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chat with Codebase',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF1E1E2C),
      ),
      home: const ChatScreen(),
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _repoController = TextEditingController();
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  bool _isIngesting = false;
  bool _isSending = false;

  List<Map<String, String>> messages = [];

  final String apiUrl = "http://localhost:8080";

  Future<void> _ingestRepo() async {
    if (_repoController.text.isEmpty) return;
    setState(() => _isIngesting = true);

    try {
      final response = await http.post(
        Uri.parse('$apiUrl/ingest_repo'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'repo_url': _repoController.text}),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        _showSnackBar(data['message']);
      } else {
        _showSnackBar('Error: ${data['detail']}');
      }
    } catch (e) {
      _showSnackBar('Failed to connect to backend: $e');
    } finally {
      setState(() => _isIngesting = false);
    }
  }

  Future<void> _sendMessage() async {
    if (_messageController.text.isEmpty) return;

    final query = _messageController.text;
    setState(() {
      messages.add({'sender': 'user', 'text': query});
      _isSending = true;
      _messageController.clear();
    });

    _scrollToBottom();

    try {
      final response = await http.post(
        Uri.parse('$apiUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'query': query,
          'filters': {'repo_url': _repoController.text.trim()},
        }),
      );

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        String answer = data['answer'] ?? "No answer received.";
        if (data['citations'] != null &&
            (data['citations'] as List).isNotEmpty) {
          answer += "\n\nCitations: ${(data['citations'] as List).join(', ')}";
        }
        setState(() {
          messages.add({'sender': 'ai', 'text': answer});
        });
      } else {
        setState(() {
          messages.add({'sender': 'ai', 'text': 'Error: ${data['detail']}'});
        });
      }
    } catch (e) {
      setState(() {
        messages.add({'sender': 'ai', 'text': 'Failed to connect to backend.'});
      });
    } finally {
      setState(() => _isSending = false);
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Chat with Codebase'),
        backgroundColor: const Color(0xFF2A2A3E),
        elevation: 0,
      ),
      body: Row(
        children: [
          // Sidebar
          Container(
            width: 300,
            color: const Color(0xFF2A2A3E),
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "Ingest Repository",
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _repoController,
                  decoration: InputDecoration(
                    labelText: 'GitHub Repository URL',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                    filled: true,
                    fillColor: const Color(0xFF1E1E2C),
                  ),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isIngesting ? null : _ingestRepo,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.blueAccent,
                    ),
                    child: _isIngesting
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : const Text('Ingest Repo'),
                  ),
                ),
                const Spacer(),
                const Text(
                  "Metadata Filters",
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                const Text(
                  "Filtering coming soon...",
                  style: TextStyle(color: Colors.grey),
                ),
              ],
            ),
          ),
          // Main Chat Area
          Expanded(
            child: Column(
              children: [
                Expanded(
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: messages.length,
                    itemBuilder: (context, index) {
                      final msg = messages[index];
                      final isUser = msg['sender'] == 'user';
                      return Align(
                        alignment: isUser
                            ? Alignment.centerRight
                            : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.all(16),
                          constraints: BoxConstraints(
                            maxWidth: MediaQuery.of(context).size.width * 0.5,
                          ),
                          decoration: BoxDecoration(
                            color: isUser
                                ? Colors.blueAccent
                                : const Color(0xFF2A2A3E),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            msg['text']!,
                            style: const TextStyle(fontSize: 16, height: 1.4),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                if (_isSending)
                  const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: CircularProgressIndicator(),
                  ),
                Container(
                  padding: const EdgeInsets.all(16),
                  color: const Color(0xFF2A2A3E),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _messageController,
                          decoration: InputDecoration(
                            hintText: 'Ask a question about the codebase...',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: BorderSide.none,
                            ),
                            filled: true,
                            fillColor: const Color(0xFF1E1E2C),
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 20,
                              vertical: 16,
                            ),
                          ),
                          onSubmitted: (_) => _sendMessage(),
                        ),
                      ),
                      const SizedBox(width: 12),
                      CircleAvatar(
                        radius: 24,
                        backgroundColor: Colors.blueAccent,
                        child: IconButton(
                          icon: const Icon(Icons.send, color: Colors.white),
                          onPressed: _sendMessage,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
