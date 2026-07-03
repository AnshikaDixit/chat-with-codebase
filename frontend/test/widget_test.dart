import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/main.dart';
// import 'package:mockito/mockito.dart';
// import 'package:mockito/annotations.dart';
// import 'package:http/http.dart' as http;

// TDD Note: When you extract your API calls to an ApiClient class, 
// you can generate mocks using: @GenerateMocks([ApiClient])
// and then use it here to ensure UI tests don't hit the real backend.

void main() {
  testWidgets('Chat interface has title and input fields', (WidgetTester tester) async {
    // TDD Note: Inject your MockApiClient into MyApp when testing
    // final mockClient = MockApiClient();
    // await tester.pumpWidget(MyApp(apiClient: mockClient));
    
    await tester.pumpWidget(const MyApp());

    // Verify that our title is present
    expect(find.text('Chat with Codebase'), findsOneWidget);

    // Verify that we have a URL input field
    expect(find.byType(TextField), findsWidgets);
    expect(find.text('GitHub Repository URL'), findsOneWidget);

    // Verify that we have an Ingest button
    expect(find.text('Ingest Repo'), findsOneWidget);
  });
}
