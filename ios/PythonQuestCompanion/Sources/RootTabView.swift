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
    @State private var usingFallback = false
    @State private var showingSetup = false

    var body: some View {
        NavigationStack {
            ZStack {
                if let primaryURL = settings.primaryWorkspaceURL(for: workspace) {
                    CompanionWebView(
                        primaryURL: primaryURL,
                        fallbackURL: settings.fallbackWorkspaceURL(for: workspace),
                        isLoading: $isLoading,
                        loadError: $loadError,
                        usingFallback: $usingFallback
                    )
                    .id(reloadToken)
                    .ignoresSafeArea(edges: .bottom)
                } else {
                    ContentUnavailableView(
                        "Invalid URL",
                        systemImage: "wifi.exclamationmark",
                        description: Text("Open Setup and choose Auto Sync, On Device, or enter a valid hosted/local server URL.")
                    )
                }

                if let notice = connectionNotice {
                    VStack {
                        Spacer()
                        ConnectionNotice(title: notice.title, message: notice.message) {
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
                        usingFallback = false
                        reloadToken = UUID()
                    }
                }
            }
            .sheet(isPresented: $showingSetup) {
                SetupView(settings: settings)
            }
        }
    }

    private var connectionNotice: (title: String, message: String)? {
        if settings.usesLocalhost && !DeviceContext.isSimulator {
            return (
                "Localhost won't work",
                "This iPhone cannot use localhost for your Mac-hosted server. Switch to Auto Sync, the hosted Render URL, or your Mac's LAN IP in Setup."
            )
        }

        if usingFallback && settings.usesAutomaticSync {
            return (
                "Using on-device fallback",
                "The hosted site could not be reached, so this tab switched to the bundled iPhone copy. Future web deploys will show up here again as soon as the hosted site is reachable."
            )
        }

        if let loadError {
            return ("Connection issue", loadError)
        }

        return nil
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
                            Text("Auto Sync is the recommended mode for one-prompt feature shipping. It points the app at the deployed website first, then falls back to the bundled offline copy if Render is unavailable.")
                                .foregroundStyle(.secondary)

                            VStack(alignment: .leading, spacing: 6) {
                                Text("Current mode")
                                    .font(.subheadline.weight(.semibold))
                                Text(settings.connectionMode.title)
                                    .font(.headline)
                                Text(settings.connectionMode.summary)
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                            }

                            VStack(alignment: .leading, spacing: 8) {
                                Text("Custom server URL")
                                    .font(.subheadline.weight(.semibold))
                                TextField("https://interview-prep-96ol.onrender.com", text: customServerBinding)
                                    .textInputAutocapitalization(.never)
                                    .autocorrectionDisabled()
                                    .padding(12)
                                    .background(Color.white)
                                    .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                            }

                            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                                ModeChoiceButton(
                                    title: "Auto Sync",
                                    isActive: settings.connectionMode == .automatic,
                                    action: { settings.useAutomaticSync() }
                                )
                                ModeChoiceButton(
                                    title: "On Device",
                                    isActive: settings.connectionMode == .onDevice,
                                    action: { settings.useOnDeviceMode() }
                                )
                                ModeChoiceButton(
                                    title: "Hosted",
                                    isActive: settings.connectionMode == .manual && !settings.usesLocalhost,
                                    action: { settings.useHostedSite() }
                                )
                                ModeChoiceButton(
                                    title: "Localhost",
                                    isActive: settings.usesLocalhost,
                                    action: { settings.useLocalhost() }
                                )
                            }

                            if settings.usesLocalhost && !DeviceContext.isSimulator {
                                Text("`localhost` on a real iPhone points to the phone itself, not your Mac. Use Auto Sync, the hosted site, or your Mac's LAN IP instead.")
                                    .font(.footnote)
                                    .foregroundStyle(.red)
                            }
                        }
                    }

                    CompanionCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("Auto Sync")
                                .font(.headline)
                            Text(settings.hostedBaseURLString)
                                .font(.system(.footnote, design: .monospaced))
                                .textSelection(.enabled)
                            Text("Best for shipping from your iPhone. Web deploys show up in the app without rebuilding, and the bundled on-device copy still works when the website is down.")
                                .foregroundStyle(.secondary)
                        }
                    }

                    CompanionCard {
                        VStack(alignment: .leading, spacing: 10) {
                            Text("On-device mode")
                                .font(.headline)
                            Text(settings.onDeviceBaseURLString)
                                .font(.system(.footnote, design: .monospaced))
                                .textSelection(.enabled)
                            Text("Quest, Lab, and the interview browser run from bundled assets with local lesson data and an on-device Python validator.")
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
                            Text("Quest loads `?workspace=quest` and Lab loads `?workspace=python`, so the iOS shell stays aligned with the same product surface whether it runs from the deployed site, a custom server, or the bundled app.")
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

    private var customServerBinding: Binding<String> {
        Binding(
            get: { settings.baseURLString },
            set: { newValue in
                settings.baseURLString = newValue
                settings.useCustomServer()
            }
        )
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

struct ModeChoiceButton: View {
    let title: String
    let isActive: Bool
    let action: () -> Void

    var body: some View {
        Group {
            if isActive {
                Button(action: action) {
                    Text(title)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
            } else {
                Button(action: action) {
                    Text(title)
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            }
        }
    }
}

struct ConnectionNotice: View {
    let title: String
    let message: String
    let onOpenSetup: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label(title, systemImage: "wifi.exclamationmark")
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
