import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/main.dart';

void main() {
  testWidgets('Chat interface has title and input fields', (WidgetTester tester) async {
    // Build our app and trigger a frame.
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
