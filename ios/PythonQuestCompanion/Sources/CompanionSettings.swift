import Foundation
import Observation

enum CompanionWorkspace: String, CaseIterable, Identifiable {
    case quest
    case lab

    var id: String { rawValue }

    var queryValue: String {
        switch self {
        case .quest:
            return "quest"
        case .lab:
            return "python"
        }
    }

    var navigationTitle: String {
        switch self {
        case .quest:
            return "Quest"
        case .lab:
            return "CLI Lab"
        }
    }

    var heading: String {
        switch self {
        case .quest:
            return "Python Quest Academy"
        case .lab:
            return "Python Interactive Lab"
        }
    }

    var symbolName: String {
        switch self {
        case .quest:
            return "gamecontroller"
        case .lab:
            return "terminal"
        }
    }
}

enum CompanionConnectionMode: String, CaseIterable, Identifiable {
    case automatic
    case onDevice
    case manual

    var id: String { rawValue }

    var title: String {
        switch self {
        case .automatic:
            return "Auto Sync"
        case .onDevice:
            return "On Device"
        case .manual:
            return "Custom Server"
        }
    }

    var summary: String {
        switch self {
        case .automatic:
            return "Loads the deployed site first and falls back to the bundled iPhone copy if the website is unavailable."
        case .onDevice:
            return "Runs the bundled site, lesson data, and Python validator directly on the iPhone."
        case .manual:
            return "Targets a specific hosted URL or localhost server that you enter manually."
        }
    }
}

@MainActor
@Observable
final class CompanionSettings {
    private static let connectionModeKey = "companion.connection_mode"
    private static let baseURLKey = "companion.base_url"
    private static let onDeviceBaseURL = "app://local/index.html"
    private static let fallbackHostedBaseURL = "https://interview-prep.onrender.com"

    var connectionMode: CompanionConnectionMode {
        didSet {
            UserDefaults.standard.set(connectionMode.rawValue, forKey: Self.connectionModeKey)
        }
    }

    var baseURLString: String {
        didSet {
            UserDefaults.standard.set(baseURLString, forKey: Self.baseURLKey)
        }
    }

    init() {
        let storedBaseURL = UserDefaults.standard.string(forKey: Self.baseURLKey)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        let storedMode = UserDefaults.standard.string(forKey: Self.connectionModeKey)

        if let storedMode, let parsedMode = CompanionConnectionMode(rawValue: storedMode) {
            connectionMode = parsedMode
            baseURLString = storedBaseURL?.isEmpty == false ? storedBaseURL! : Self.defaultHostedBaseURL
            return
        }

        if storedBaseURL == nil || storedBaseURL == Self.onDeviceBaseURL {
            connectionMode = .automatic
            baseURLString = Self.defaultHostedBaseURL
            return
        }

        connectionMode = .manual
        baseURLString = storedBaseURL!
    }

    static var defaultHostedBaseURL: String {
        let bundled = (Bundle.main.object(forInfoDictionaryKey: "CompanionDefaultBaseURL") as? String)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return bundled?.isEmpty == false ? bundled! : fallbackHostedBaseURL
    }

    var trimmedBaseURL: String {
        baseURLString.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var manualBaseURL: URL? {
        Self.url(from: trimmedBaseURL)
    }

    var hostedBaseURLString: String {
        Self.defaultHostedBaseURL
    }

    var onDeviceBaseURLString: String {
        Self.onDeviceBaseURL
    }

    var usesAutomaticSync: Bool {
        connectionMode == .automatic
    }

    var usesOnDeviceApp: Bool {
        connectionMode == .onDevice
    }

    var usesLocalhost: Bool {
        guard connectionMode == .manual, let host = manualBaseURL?.host?.lowercased() else {
            return false
        }
        return host == "localhost" || host == "127.0.0.1" || host == "::1"
    }

    func primaryWorkspaceURL(for workspace: CompanionWorkspace) -> URL? {
        switch connectionMode {
        case .automatic:
            return workspaceURL(baseString: hostedBaseURLString, workspace: workspace)
        case .onDevice:
            return workspaceURL(baseString: onDeviceBaseURLString, workspace: workspace)
        case .manual:
            return workspaceURL(baseURL: manualBaseURL, workspace: workspace)
        }
    }

    func fallbackWorkspaceURL(for workspace: CompanionWorkspace) -> URL? {
        guard connectionMode == .automatic else {
            return nil
        }
        return workspaceURL(baseString: onDeviceBaseURLString, workspace: workspace)
    }

    func useAutomaticSync() {
        connectionMode = .automatic
    }

    func useCustomServer() {
        connectionMode = .manual
    }

    func useLocalhost() {
        baseURLString = "http://localhost:8000"
        connectionMode = .manual
    }

    func useOnDeviceMode() {
        connectionMode = .onDevice
    }

    func useHostedSite() {
        baseURLString = Self.defaultHostedBaseURL
        connectionMode = .manual
    }

    private func workspaceURL(baseString: String, workspace: CompanionWorkspace) -> URL? {
        workspaceURL(baseURL: Self.url(from: baseString), workspace: workspace)
    }

    private func workspaceURL(baseURL: URL?, workspace: CompanionWorkspace) -> URL? {
        guard let baseURL, var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else {
            return nil
        }

        var queryItems = components.queryItems ?? []
        queryItems.removeAll { item in
            item.name == "workspace" || item.name == "lesson"
        }
        queryItems.append(URLQueryItem(name: "workspace", value: workspace.queryValue))
        components.queryItems = queryItems
        return components.url
    }

    private static func url(from baseString: String) -> URL? {
        let trimmed = baseString.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            return nil
        }

        if let url = URL(string: trimmed), url.scheme != nil {
            return url
        }

        return URL(string: "http://\(trimmed)")
    }
}
