import XCTest

final class CanonR5ReferenceUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    func testApplicationLaunchesAndHomePageLoads() throws {
        let app = XCUIApplication()
        app.launch()

        XCTAssertTrue(app.webViews["referenceWebView"].waitForExistence(timeout: 10))
        XCTAssertTrue(app.staticTexts["Photography Cards"].waitForExistence(timeout: 10))
    }

    func testSampleNavigationAndBack() throws {
        let app = XCUIApplication()
        app.launch()

        XCTAssertTrue(app.staticTexts["Photography Cards"].waitForExistence(timeout: 10))
        let firstCard = app.staticTexts["Birds in Flight"]
        if firstCard.waitForExistence(timeout: 5) {
            firstCard.tap()
            XCTAssertTrue(app.images.firstMatch.waitForExistence(timeout: 5))
            app.swipeRight()
        }
    }

    func testSearchIfPresent() throws {
        let app = XCUIApplication()
        app.launch()

        let searchField = app.searchFields.firstMatch
        if searchField.waitForExistence(timeout: 3) {
            searchField.tap()
            searchField.typeText("focus")
            XCTAssertTrue(app.staticTexts.containing(NSPredicate(format: "label CONTAINS[c] %@", "focus")).firstMatch.waitForExistence(timeout: 5))
        }
    }
}
