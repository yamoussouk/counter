  fetch("config/")
      .then((e) => e.json())
      .then((e) => {
          const c = Stripe(e.publicKey);
          document.querySelector("#submitBtn").addEventListener("click", () => {
              document.querySelector("#aszf-check").checked &&
                  fetch("create-checkout-session/")
                      .then((e) => e.json())
                      .then((e) => (console.log(e), c.redirectToCheckout({ sessionId: e.sessionId })))
                      .then((e) => {
                          console.log(e);
                      });
          });
      });
