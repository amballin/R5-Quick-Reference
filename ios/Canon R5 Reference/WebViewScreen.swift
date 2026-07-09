import SwiftUI
import WebKit

struct WebViewScreen: View {
    var body: some View {
        ReferenceWebView()
            .ignoresSafeArea(.keyboard)
            .background(Color(.systemBackground))
    }
}

struct ReferenceWebView: UIViewRepresentable {
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true

        let userContentController = WKUserContentController()
        userContentController.add(context.coordinator, name: "jsError")
        userContentController.addUserScript(Self.javascriptErrorBridge)
        configuration.userContentController = userContentController

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.contentInsetAdjustmentBehavior = .automatic
        webView.isOpaque = false
        webView.backgroundColor = .systemBackground
        webView.scrollView.backgroundColor = .systemBackground
        webView.accessibilityIdentifier = "referenceWebView"
        context.coordinator.webView = webView
        loadIndex(in: webView)
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    private func loadIndex(in webView: WKWebView) {
        guard let websiteURL = Bundle.main.url(forResource: "Website", withExtension: nil),
              let indexURL = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "Website") else {
            webView.loadHTMLString(Self.errorHTML("The bundled Website/index.html file could not be found."), baseURL: nil)
            return
        }

        webView.loadFileURL(indexURL, allowingReadAccessTo: websiteURL)
    }

    private static let javascriptErrorBridge = WKUserScript(
        source: """
        window.__canonR5ReferenceErrors = [];
        window.addEventListener('error', function(event) {
          window.__canonR5ReferenceErrors.push(event.message || 'JavaScript error');
          window.webkit.messageHandlers.jsError.postMessage(event.message || 'JavaScript error');
        });
        window.addEventListener('unhandledrejection', function(event) {
          var reason = event.reason && event.reason.message ? event.reason.message : String(event.reason);
          window.__canonR5ReferenceErrors.push(reason || 'Unhandled promise rejection');
          window.webkit.messageHandlers.jsError.postMessage(reason || 'Unhandled promise rejection');
        });
        """,
        injectionTime: .atDocumentStart,
        forMainFrameOnly: false
    )

    private static func errorHTML(_ message: String) -> String {
        """
        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
        <style>
        :root { color-scheme: light dark; }
        body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; font: -apple-system-body; background: Canvas; color: CanvasText; }
        main { max-width: 34rem; }
        h1 { font: -apple-system-title1; margin: 0 0 10px; }
        p { margin: 0; line-height: 1.45; }
        </style>
        </head>
        <body>
        <main>
        <h1>Reference could not be loaded</h1>
        <p>\(message)</p>
        </main>
        </body>
        </html>
        """
    }
}

final class Coordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
    weak var webView: WKWebView?
    private(set) var javaScriptErrors: [String] = []

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        webView.loadHTMLString(ReferenceWebViewErrorPage.html(error.localizedDescription), baseURL: nil)
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        webView.loadHTMLString(ReferenceWebViewErrorPage.html(error.localizedDescription), baseURL: nil)
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else {
            decisionHandler(.allow)
            return
        }

        if url.isFileURL || url.scheme == "about" {
            decisionHandler(.allow)
            return
        }

        if ["http", "https", "tel", "mailto"].contains(url.scheme?.lowercased()) {
            UIApplication.shared.open(url)
            decisionHandler(.cancel)
            return
        }

        decisionHandler(.allow)
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "jsError" else { return }
        javaScriptErrors.append(String(describing: message.body))
    }
}

private enum ReferenceWebViewErrorPage {
    static func html(_ message: String) -> String {
        """
        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
        <style>
        :root { color-scheme: light dark; }
        body { margin: 0; min-height: 100vh; display: grid; place-items: center; padding: 24px; font: -apple-system-body; background: Canvas; color: CanvasText; }
        main { max-width: 34rem; }
        h1 { font: -apple-system-title1; margin: 0 0 10px; }
        p { margin: 0; line-height: 1.45; }
        </style>
        </head>
        <body>
        <main>
        <h1>Reference could not be loaded</h1>
        <p>\(message)</p>
        </main>
        </body>
        </html>
        """
    }
}
