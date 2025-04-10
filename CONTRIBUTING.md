# Contributing to Shooting Star

First off, thank you for considering contributing to Shooting Star! It's people like you that make Shooting Star such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold a moral code of conduct. Please report unacceptable behavior to omgupta0720@gmail.com

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for Shooting Star. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

Before creating bug reports, please check [the issue list](https://github.com/OmGuptaIND/shooting-star/issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible.

#### How Do I Submit A Bug Report?

Bugs are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if possible
* Include details about your configuration and environment

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Shooting Star, including completely new features and minor improvements to existing functionality.

#### How Do I Submit An Enhancement Suggestion?

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide the following information:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful to most Shooting Star users
* List some other tools or applications where this enhancement exists, if applicable
* Include screenshots or mockups if applicable

### Your First Code Contribution

Unsure where to begin contributing to Shooting Star? You can start by looking through these `beginner-friendly` and `help-wanted` issues:

* [Beginner friendly issues](https://github.com/OmGuptaIND/shooting-star/labels/beginner-friendly) - issues which should only require a few lines of code and a test or two
* [Help wanted issues](https://github.com/OmGuptaIND/shooting-star/labels/help-wanted) - issues which should be a bit more involved than beginner issues

### Pull Requests

The process described here has several goals:

* Maintain Shooting Star's quality
* Fix problems that are important to users
* Engage the community in working toward the best possible Shooting Star
* Enable a sustainable system for Shooting Star's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow the [styleguides](#styleguides)
2. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐎 `:racehorse:` when improving performance
    * 🔍 `:mag:` when improving search functionality
    * 📝 `:memo:` when writing docs
    * 🐛 `:bug:` when fixing a bug
    * 🔥 `:fire:` when removing code or files
    * 💚 `:green_heart:` when fixing the CI build
    * ✅ `:white_check_mark:` when adding tests
    * 🔒 `:lock:` when dealing with security
    * ⬆️ `:arrow_up:` when upgrading dependencies
    * ⬇️ `:arrow_down:` when downgrading dependencies
    * 👕 `:shirt:` when removing linter warnings

### Go Styleguide

* Follow the [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
* Ensure your code passes `golangci-lint run`
* Handle errors explicitly; don't use `_` to ignore errors
* Use the custom `AppError` interface from the appError package
* Group imports: standard library, external packages, and internal packages
* Use descriptive variable names; short variable names are acceptable in short-lived blocks

### JavaScript/TypeScript Styleguide

* All JavaScript/TypeScript code is formatted with Biome
* Use tabs for indentation
* Use double quotes for strings
* Use template literals when interpolating variables
* Prefer the object spread operator (`{...anotherObj}`) to `Object.assign()`
* Use the function syntax that is most appropriate for the task
* Avoid using `any` type in TypeScript; use proper types or generics
* Use React hooks and functional components instead of class components
* Organize imports with the Biome organizeImports feature

### CSS/Styling Styleguide

* Use Tailwind CSS classes for styling
* Use the class-variance-authority package for component variants
* Follow the component/UI pattern for component structure
* Use the tailwind-merge package for merging Tailwind classes

### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown)
* Reference methods and classes in markdown with the custom `{...}` notation:
    * Reference methods: `{Class#method}`
    * Reference a class: `{Class}`
* Include code examples where appropriate
* Keep documentation up-to-date with code changes

## Technical Architecture Overview

For those wanting to dive deeper into the architecture before contributing:

### Backend (Go)

* HTTP server built with Fiber
* PostgreSQL database with pgvector extension for vector embeddings
* GORM for database operations
* Pipeline architecture for processing different data types
* Custom error handling via AppError interface

### Frontend (Next.js)

* Next.js application with App Router
* tRPC for type-safe API communication
* Jotai for state management
* Tailwind CSS with Radix UI components
* Block-based document rendering system

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* `bug` - Issues that are bugs
* `enhancement` - Issues that are feature requests
* `documentation` - Issues relating to documentation
* `good-first-issue` - Good for newcomers
* `help-wanted` - Extra attention is needed
* `question` - Further information is requested
* `wontfix` - This will not be worked on

Thank you for your interest in contributing to Shooting Star!