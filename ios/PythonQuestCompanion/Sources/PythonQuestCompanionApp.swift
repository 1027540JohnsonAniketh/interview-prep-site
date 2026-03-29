import SwiftUI

@main
struct PythonQuestCompanionApp: App {
    @State private var settings = CompanionSettings()

    var body: some Scene {
        WindowGroup {
            RootTabView(settings: settings)
        }
    }
}
