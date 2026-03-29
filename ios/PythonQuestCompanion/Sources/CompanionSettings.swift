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

@MainActor
@Observable
final class CompanionSettings {
    private static let baseURLKey = "companion.base_url"
    private static let onDeviceBaseURL = "app://local/index.html"
    private static let fallbackHostedBaseURL = "https://interview-prep.onrender.com"

    var baseURLString: String {
        didSet {
            UserDefaults.standard.set(baseURLString, forKey: Self.baseURLKey)
        }
    }

    init() {
        let stored = UserDefaults.standard.string(forKey: Self.baseURLKey)
        self.baseURLString = stored?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false
            ? stored!
            : Self.onDeviceBaseURL
    }

    static var defaultHostedBaseURL: String {
        let bundled = (Bundle.main.object(forInfoDictionaryKey: "CompanionDefaultBaseURL") as? String)?
            .trimmingCharacters(in: .whitespacesAndNewlines)
        return bundled?.isEmpty == false ? bundled! : fallbackHostedBaseURL
    }

    var trimmedBaseURL: String {
        baseURLString.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var baseURL: URL? {
        guard !trimmedBaseURL.isEmpty else {
            return nil
        }

        if let url = URL(string: trimmedBaseURL), url.scheme != nil {
            return url
        }

        return URL(string: "http://\(trimmedBaseURL)")
    }

    var hostedBaseURLString: String {
        Self.defaultHostedBaseURL
    }

    var onDeviceBaseURLString: String {
        Self.onDeviceBaseURL
    }

    var usesOnDeviceApp: Bool {
        baseURL?.scheme?.lowercased() == "app"
    }

    var usesLocalhost: Bool {
        guard let host = baseURL?.host?.lowercased() else {
            return false
        }
        return host == "localhost" || host == "127.0.0.1" || host == "::1"
    }

    func workspaceURL(for workspace: CompanionWorkspace) -> URL? {
        guard let baseURL else {
            return nil
        }

        guard var components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false) else {
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

    func useLocalhost() {
        baseURLString = "http://localhost:8000"
    }

    func useOnDeviceMode() {
        baseURLString = Self.onDeviceBaseURL
    }

    func useHostedSite() {
        baseURLString = Self.defaultHostedBaseURL
    }
}
