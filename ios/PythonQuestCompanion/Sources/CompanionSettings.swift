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

    var summary: String {
        switch self {
        case .quest:
            return "Open the browser game workspace directly, with the route pinned to the quest view."
        case .lab:
            return "Jump into the original interactive lesson CLI, now embedded in the app."
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

    var baseURLString: String {
        didSet {
            UserDefaults.standard.set(baseURLString, forKey: Self.baseURLKey)
        }
    }

    init() {
        let stored = UserDefaults.standard.string(forKey: Self.baseURLKey)
        self.baseURLString = stored?.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty == false
            ? stored!
            : "http://localhost:8000"
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
}
