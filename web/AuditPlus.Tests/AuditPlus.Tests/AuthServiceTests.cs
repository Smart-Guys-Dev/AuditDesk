using AuditPlus.Application.DTOs;
using AuditPlus.Application.Interfaces;
using AuditPlus.Application.Services;
using AuditPlus.Application.Settings;
using AuditPlus.Domain.Entities;
using AuditPlus.Domain.Interfaces;
using Microsoft.Extensions.Options;
using Moq;

namespace AuditPlus.Tests;

/// <summary>
/// Testes unitários do AuthService.
/// Cobre: login, lockout, password validation, registro.
/// </summary>
public class AuthServiceTests
{
    private readonly Mock<IUserRepository> _userRepoMock;
    private readonly AuthService _authService;

    public AuthServiceTests()
    {
        _userRepoMock = new Mock<IUserRepository>();
        
        var passwordHasher = new BcryptPasswordHasher();
        
        var jwtSettings = Options.Create(new JwtSettings
        {
            SecretKey = "TestSecretKeyThatIsLongEnoughForHmacSha256Signing!",
            Issuer = "TestIssuer",
            Audience = "TestAudience",
            ExpirationHours = 1
        });

        _authService = new AuthService(_userRepoMock.Object, passwordHasher, jwtSettings);
    }

    // ========================================
    // LOGIN — Sucesso
    // ========================================
    
    [Fact]
    public async Task LoginAsync_ValidCredentials_ReturnsToken()
    {
        // Arrange
        var user = CreateTestUser("admin", "Test@1234");
        _userRepoMock.Setup(r => r.GetByUsernameAsync("admin")).ReturnsAsync(user);

        var request = new LoginRequest("admin", "Test@1234");

        // Act
        var result = await _authService.LoginAsync(request);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("admin", result.Username);
        Assert.False(string.IsNullOrEmpty(result.Token));
        
        // Verify reset of failed attempts
        _userRepoMock.Verify(r => r.UpdateAsync(It.Is<User>(u =>
            u.FailedLoginAttempts == 0 && u.LockedUntil == null)), Times.Once);
    }

    // ========================================
    // LOGIN — Falhas
    // ========================================

    [Fact]
    public async Task LoginAsync_WrongPassword_ReturnsNull()
    {
        // Arrange
        var user = CreateTestUser("admin", "Test@1234");
        _userRepoMock.Setup(r => r.GetByUsernameAsync("admin")).ReturnsAsync(user);

        var request = new LoginRequest("admin", "WrongPassword!");

        // Act
        var result = await _authService.LoginAsync(request);

        // Assert
        Assert.Null(result);
        _userRepoMock.Verify(r => r.UpdateAsync(It.Is<User>(u =>
            u.FailedLoginAttempts == 1)), Times.Once);
    }

    [Fact]
    public async Task LoginAsync_UserNotFound_ReturnsNull()
    {
        _userRepoMock.Setup(r => r.GetByUsernameAsync("unknown")).ReturnsAsync((User?)null);

        var result = await _authService.LoginAsync(new LoginRequest("unknown", "any"));

        Assert.Null(result);
    }

    [Fact]
    public async Task LoginAsync_InactiveUser_ReturnsNull()
    {
        var user = CreateTestUser("admin", "Test@1234");
        user.IsActive = false;
        _userRepoMock.Setup(r => r.GetByUsernameAsync("admin")).ReturnsAsync(user);

        var result = await _authService.LoginAsync(new LoginRequest("admin", "Test@1234"));

        Assert.Null(result);
    }

    // ========================================
    // LOGIN — Lockout (OWASP A07)
    // ========================================

    [Fact]
    public async Task LoginAsync_LockedAccount_ReturnsNull()
    {
        var user = CreateTestUser("admin", "Test@1234");
        user.LockedUntil = DateTime.UtcNow.AddMinutes(10); // still locked
        _userRepoMock.Setup(r => r.GetByUsernameAsync("admin")).ReturnsAsync(user);

        var result = await _authService.LoginAsync(new LoginRequest("admin", "Test@1234"));

        Assert.Null(result);
    }

    [Fact]
    public async Task LoginAsync_5thFailedAttempt_LocksAccount()
    {
        var user = CreateTestUser("admin", "Test@1234");
        user.FailedLoginAttempts = 4; // 4 previous failures
        _userRepoMock.Setup(r => r.GetByUsernameAsync("admin")).ReturnsAsync(user);

        var result = await _authService.LoginAsync(new LoginRequest("admin", "WrongPw!"));

        Assert.Null(result);
        _userRepoMock.Verify(r => r.UpdateAsync(It.Is<User>(u =>
            u.FailedLoginAttempts == 5 && u.LockedUntil.HasValue)), Times.Once);
    }

    [Fact]
    public async Task LoginAsync_ExpiredLockout_AllowsLogin()
    {
        var user = CreateTestUser("admin", "Test@1234");
        user.LockedUntil = DateTime.UtcNow.AddMinutes(-1); // expired
        user.FailedLoginAttempts = 5;
        _userRepoMock.Setup(r => r.GetByUsernameAsync("admin")).ReturnsAsync(user);

        var result = await _authService.LoginAsync(new LoginRequest("admin", "Test@1234"));

        Assert.NotNull(result);
        _userRepoMock.Verify(r => r.UpdateAsync(It.Is<User>(u =>
            u.FailedLoginAttempts == 0 && u.LockedUntil == null)), Times.Once);
    }

    // ========================================
    // REGISTER — Validações
    // ========================================

    [Fact]
    public async Task RegisterAsync_ValidData_ReturnsUser()
    {
        _userRepoMock.Setup(r => r.UsernameExistsAsync("newuser")).ReturnsAsync(false);
        _userRepoMock.Setup(r => r.AddAsync(It.IsAny<User>()))
            .ReturnsAsync((User u) => { u.Id = 1; return u; });

        var request = new RegisterRequest("newuser", "Strong@Pass1", "New User", "new@email.com", "Auditor");
        var result = await _authService.RegisterAsync(request);

        Assert.NotNull(result);
        Assert.Equal("newuser", result.Username);
    }

    [Fact]
    public async Task RegisterAsync_DuplicateUsername_ReturnsNull()
    {
        _userRepoMock.Setup(r => r.UsernameExistsAsync("existing")).ReturnsAsync(true);

        var request = new RegisterRequest("existing", "Strong@Pass1", "Existing", "e@m.com", "Auditor");
        var result = await _authService.RegisterAsync(request);

        Assert.Null(result);
    }

    [Fact]
    public async Task RegisterAsync_WeakPassword_ThrowsArgumentException()
    {
        _userRepoMock.Setup(r => r.UsernameExistsAsync("newuser")).ReturnsAsync(false);

        var request = new RegisterRequest("newuser", "weak", "New User", "new@email.com", "Auditor");

        await Assert.ThrowsAsync<ArgumentException>(() => _authService.RegisterAsync(request));
    }

    // ========================================
    // CHANGE PASSWORD — Validações
    // ========================================

    [Fact]
    public async Task ChangePasswordAsync_ValidChange_ReturnsTrue()
    {
        var user = CreateTestUser("admin", "OldPass@123");
        user.Id = 1;
        _userRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(user);

        var result = await _authService.ChangePasswordAsync(1,
            new ChangePasswordRequest("OldPass@123", "NewPass@456"));

        Assert.True(result);
    }

    [Fact]
    public async Task ChangePasswordAsync_WeakNewPassword_ThrowsArgumentException()
    {
        var user = CreateTestUser("admin", "OldPass@123");
        user.Id = 1;
        _userRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(user);

        await Assert.ThrowsAsync<ArgumentException>(() =>
            _authService.ChangePasswordAsync(1,
                new ChangePasswordRequest("OldPass@123", "weak")));
    }

    [Fact]
    public async Task ChangePasswordAsync_WrongCurrentPassword_ReturnsFalse()
    {
        var user = CreateTestUser("admin", "OldPass@123");
        user.Id = 1;
        _userRepoMock.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(user);

        var result = await _authService.ChangePasswordAsync(1,
            new ChangePasswordRequest("WrongCurrent!", "NewPass@456"));

        Assert.False(result);
    }

    // ========================================
    // Helper
    // ========================================

    private static User CreateTestUser(string username, string password)
    {
        return new User
        {
            Id = 1,
            Username = username,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(password),
            FullName = "Test User",
            Email = "test@test.com",
            Role = Domain.Enums.UserRole.ADMIN,
            IsActive = true,
            CreatedAt = DateTime.UtcNow
        };
    }
}
