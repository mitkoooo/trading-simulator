describe("Login Page", () => {
  beforeEach(() => {
    cy.request("POST", "localhost:8000/v1/users/logout");
  });

  it("Should redirect to login page if not authorized", () => {
    cy.visit("/");
    cy.url().should("include", "/login");
  });

  it("Should login traders 1", () => {
    cy.visit("/login");
    cy.get("input[name=trader_id]").type("1{enter}");
    cy.url().should("equal", "http://localhost:3000/");
  });

  it("Should login traders 2", () => {
    cy.visit("/login");
    cy.get("input[name=trader_id]").type("2{enter}");
    cy.url().should("equal", "http://localhost:3000/");
  });
});
