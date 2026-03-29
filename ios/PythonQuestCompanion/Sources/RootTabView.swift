import Observation
import SwiftUI

struct RootTabView: View {
    @Bindable var settings: CompanionSettings

    var body: some View {
        TabView {
            WorkspaceHostView(settings: settings, workspace: .quest)
                .tabItem {
                    Label("Quest", systemImage: CompanionWorkspace.quest.symbolName)
                }

            WorkspaceHostView(settings: settings, workspace: .lab)
                .tabItem {
                    Label("Lab", systemImage: CompanionWorkspace.lab.symbolName)
                }

            SetupView(settings: settings)
                .tabItem {
                    Label("Setup", systemImage: "slider.horizontal.3")
                }
        }
    }
}

struct WorkspaceHostView: View {
    @Bindable var settings: CompanionSettings
    let workspace: CompanionWorkspace

    @State private var reloadToken = UUID()

    var body: some View {
        NavigationStack {
            VStack(spacing: 16) {
                CompanionCard {
                    VStack(alignment: .leading, spacing: 10) {
                        Text(workspace.heading)
                            .font(.title3.weight(.semibold))
                        Text(workspace.summary)
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        Text(settings.workspaceURL(for: workspace)?.absoluteString ?? "Enter a valid base URL in Setup.")
                            .font(.system(.footnote, design: .monospaced))
                            .foregroundStyle(.secondary)
                            .textSelection(.enabled)
                    }
                }

                if let url = settings.workspaceURL(for: workspace) {
                    CompanionWebView(url: url)
                        .id(reloadToken)
                        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
                        .overlay {
                            RoundedRectangle(cornerRadius: 24, style: .continuous)
                                .stroke(Color.primary.opacity(0.08), lineWidth: 1)
                        }
                } else {
                    CompanionCard {
                        Text("Set a valid base URL to load the workspace.")
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .padding()
            .background(
                LinearGradient(
                    colors: [Color(red: 0.96, green: 0.98, blue: 0.97), Color(red: 1.0, green: 0.97, blue: 0.93)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
            )
            .navigationTitle(workspace.navigationTitle)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Reload") {
                        reloadToken = UUID()
                    }
                }
            }
        }
    }
}

struct SetupView: View {
    @Bindable var settings: CompanionSettings

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    CompanionCard {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("Connection")
                                .font(.title3.weight(.semibold))
                            Text("Point the app at your local FastAPI server or a hosted deployment.")
                                .foregroundStyle(.secondary)
                            TextField("http://localhost:8000", text: $settings.baseURLString)
                                .textInputAutocapitalization(.never)
                                .autocorrectionDisabled()
                                .padding(12)
                                .background(Color.white)
                                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                            Button("Use Localhost") {
                                settings.useLocalhost()
                            }
                            .buttonStyle(.borderedProminent)
                        }
                    }

                    CompanionCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Run the local server")
                                .font(.headline)
                            Text("python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
                                .font(.system(.footnote, design: .monospaced))
                                .textSelection(.enabled)
                            Text("The Quest tab opens with ?workspace=quest. The Lab tab opens with ?workspace=python.")
                                .foregroundStyle(.secondary)
                        }
                    }

                    CompanionCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("What this app gives you")
                                .font(.headline)
                            Text("A lightweight native shell around the website so the simulator or device can jump straight into the quest mode or the CLI workspace.")
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                .padding()
            }
            .background(
                LinearGradient(
                    colors: [Color(red: 0.96, green: 0.98, blue: 0.97), Color(red: 1.0, green: 0.97, blue: 0.93)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
            )
            .navigationTitle("Setup")
        }
    }
}

struct CompanionCard<Content: View>: View {
    @ViewBuilder let content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            content
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.white.opacity(0.9))
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        .shadow(color: .black.opacity(0.06), radius: 18, y: 10)
    }
}
