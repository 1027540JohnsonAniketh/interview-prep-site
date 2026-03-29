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
    @State private var isLoading = true
    @State private var loadError: String?
    @State private var showingSetup = false

    var body: some View {
        NavigationStack {
            ZStack {
                if let url = settings.workspaceURL(for: workspace) {
                    CompanionWebView(url: url, isLoading: $isLoading, loadError: $loadError)
                        .id(reloadToken)
                        .ignoresSafeArea(edges: .bottom)
                } else {
                    ContentUnavailableView(
                        "Invalid URL",
                        systemImage: "wifi.exclamationmark",
                        description: Text("Open Setup and enter a valid hosted or local server URL.")
                    )
                }

                if let message = connectionMessage {
                    VStack {
                        Spacer()
                        ConnectionNotice(message: message) {
                            showingSetup = true
                        }
                        .padding()
                    }
                }
            }
            .background(Color(.systemBackground))
            .navigationTitle(workspace.navigationTitle)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button {
                        showingSetup = true
                    } label: {
                        Image(systemName: "slider.horizontal.3")
                    }
                }

                ToolbarItem(placement: .topBarTrailing) {
                    Button("Reload") {
                        isLoading = true
                        loadError = nil
                        reloadToken = UUID()
                    }
                }
            }
            .sheet(isPresented: $showingSetup) {
                SetupView(settings: settings)
            }
        }
    }

    private var connectionMessage: String? {
        if settings.usesLocalhost && !DeviceContext.isSimulator {
            return "This iPhone cannot use localhost for your Mac-hosted server. Switch to the hosted Render URL or your Mac's LAN IP in Setup."
        }
        return loadError
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
                            Text("Use the hosted site on a physical iPhone. Use localhost only when the app runs in the simulator on the same Mac as the server.")
                                .foregroundStyle(.secondary)
                            TextField("https://interview-prep.onrender.com", text: $settings.baseURLString)
                                .textInputAutocapitalization(.never)
                                .autocorrectionDisabled()
                                .padding(12)
                                .background(Color.white)
                                .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))

                            HStack {
                                Button("Use Hosted Site") {
                                    settings.useHostedSite()
                                }
                                .buttonStyle(.borderedProminent)

                                Button("Use Localhost") {
                                    settings.useLocalhost()
                                }
                                .buttonStyle(.bordered)
                            }

                            if settings.usesLocalhost && !DeviceContext.isSimulator {
                                Text("`localhost` on a real iPhone points to the phone itself, not your Mac. Use the hosted site or your Mac's LAN IP instead.")
                                    .font(.footnote)
                                    .foregroundStyle(.red)
                            }
                        }
                    }

                    CompanionCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Hosted site")
                                .font(.headline)
                            Text(settings.hostedBaseURLString)
                                .font(.system(.footnote, design: .monospaced))
                                .textSelection(.enabled)
                            Text("This should mirror the website exactly because Quest and Lab load the same web app with different `workspace` routes.")
                                .foregroundStyle(.secondary)
                        }
                    }

                    CompanionCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Local development")
                                .font(.headline)
                            Text("python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000")
                                .font(.system(.footnote, design: .monospaced))
                                .textSelection(.enabled)
                            Text("The simulator can use `http://localhost:8000`. A physical phone must use your Mac's LAN IP, for example `http://192.168.1.20:8000`.")
                                .foregroundStyle(.secondary)
                        }
                    }

                    CompanionCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("What the tabs load")
                                .font(.headline)
                            Text("Quest loads `?workspace=quest` and Lab loads `?workspace=python`, so the iOS app stays aligned with the exact website feature set.")
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

enum DeviceContext {
    #if targetEnvironment(simulator)
    static let isSimulator = true
    #else
    static let isSimulator = false
    #endif
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

struct ConnectionNotice: View {
    let message: String
    let onOpenSetup: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Connection issue", systemImage: "wifi.exclamationmark")
                .font(.headline)
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            Button("Open Setup", action: onOpenSetup)
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }
}
