import XCTest
@testable import Canon_R5_Reference

final class CanonR5ReferenceTests: XCTestCase {
    func testBundledWebsiteIndexExists() throws {
        let websiteURL = try XCTUnwrap(Self.websiteBundleURL())
        let indexURL = websiteURL.appendingPathComponent("index.html")
        XCTAssertTrue(FileManager.default.fileExists(atPath: indexURL.path))
    }

    private static func websiteBundleURL() -> URL? {
        Bundle.main.url(forResource: "Website", withExtension: nil)
            ?? Bundle(for: CanonR5ReferenceTests.self).url(forResource: "Website", withExtension: nil)
    }
}
