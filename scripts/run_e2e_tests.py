#!/usr/bin/env python3
"""
Script para executar testes E2E e gerar relatórios.

Uso:
    python scripts/run_e2e_tests.py
    python scripts/run_e2e_tests.py --quick
    python scripts/run_e2e_tests.py --coverage
    python scripts/run_e2e_tests.py --html-report
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime


# Cores para output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Imprimir cabeçalho formatado."""
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_success(text):
    """Imprimir mensagem de sucesso."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_warning(text):
    """Imprimir mensagem de aviso."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_error(text):
    """Imprimir mensagem de erro."""
    print(f"{RED}✗ {text}{RESET}")


def run_command(cmd, description):
    """Executar comando e retornar resultado."""
    print(f"\n{YELLOW}▶ {description}{RESET}")
    print(f"  Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def run_e2e_tests(args):
    """Executar testes E2E."""
    print_header("IMOOS E2E TEST SUITE")
    
    # Comando base
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/e2e/',
        '-v',
        '-m', 'e2e',
        '--tb=short',
    ]
    
    # Adicionar opções
    if args.quick:
        cmd.extend(['-m', 'e2e and not performance and not slow'])
        print_warning("Running QUICK mode (excluding performance tests)")
    
    if args.coverage:
        cmd.extend([
            '--cov=apps',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
        ])
        print_warning("Coverage report enabled")
    
    if args.html_report:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'e2e_report_{timestamp}.html'
        cmd.extend([f'--html={report_file}', '--self-contained-html'])
        print_warning(f"HTML report will be saved to: {report_file}")
    
    if args.verbose:
        cmd.append('--capture=no')
        cmd.append('-vv')
    
    # Executar
    success = run_command(cmd, "Running E2E Tests")
    
    if success:
        print_success("All E2E tests passed!")
    else:
        print_error("Some E2E tests failed!")
    
    return success


def run_tenant_isolation_tests(args):
    """Executar testes de isolamento de tenant."""
    print_header("TENANT ISOLATION TESTS")
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/tenant_isolation/',
        '-v',
        '-m', 'isolation',
        '--tb=short',
    ]
    
    if args.verbose:
        cmd.extend(['--capture=no', '-vv'])
    
    success = run_command(cmd, "Running Tenant Isolation Tests")
    
    if success:
        print_success("All isolation tests passed!")
    else:
        print_error("Some isolation tests failed!")
    
    return success


def run_integration_tests(args):
    """Executar testes de integração."""
    print_header("INTEGRATION TESTS")
    
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/integration/',
        '-v',
        '-m', 'integration',
        '--tb=short',
    ]
    
    if args.verbose:
        cmd.extend(['--capture=no', '-vv'])
    
    success = run_command(cmd, "Running Integration Tests")
    
    if success:
        print_success("All integration tests passed!")
    else:
        print_error("Some integration tests failed!")
    
    return success


def generate_summary(args, results):
    """Gerar resumo dos testes."""
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total Test Suites: {total}")
    print(f"Passed: {GREEN}{passed}{RESET}")
    print(f"Failed: {RED}{failed}{RESET}")
    
    print("\nDetailed Results:")
    for name, success in results.items():
        status = f"{GREEN}✓ PASSED{RESET}" if success else f"{RED}✗ FAILED{RESET}"
        print(f"  {name}: {status}")
    
    if args.coverage and Path('htmlcov').exists():
        print(f"\n{YELLOW}Coverage report available at: htmlcov/index.html{RESET}")
    
    print(f"\n{BLUE}{'=' * 70}{RESET}\n")
    
    return failed == 0


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description='Run ImoOS E2E Tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_e2e_tests.py
  python scripts/run_e2e_tests.py --quick
  python scripts/run_e2e_tests.py --coverage --html-report
  python scripts/run_e2e_tests.py --all
        """
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run only quick tests (exclude performance)'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '--html-report',
        action='store_true',
        help='Generate HTML test report'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all test types (e2e, isolation, integration)'
    )
    parser.add_argument(
        '--isolation-only',
        action='store_true',
        help='Run only tenant isolation tests'
    )
    parser.add_argument(
        '--e2e-only',
        action='store_true',
        help='Run only E2E tests'
    )
    
    args = parser.parse_args()
    
    # Verificar se estamos no diretório correto
    if not Path('tests/e2e').exists():
        print_error("Tests directory not found. Please run from project root.")
        sys.exit(1)
    
    results = {}
    
    if args.isolation_only:
        results['Tenant Isolation'] = run_tenant_isolation_tests(args)
    elif args.e2e_only:
        results['E2E Tests'] = run_e2e_tests(args)
    elif args.all:
        results['E2E Tests'] = run_e2e_tests(args)
        results['Tenant Isolation'] = run_tenant_isolation_tests(args)
        results['Integration Tests'] = run_integration_tests(args)
    else:
        # Padrão: rodar apenas E2E
        results['E2E Tests'] = run_e2e_tests(args)
    
    # Gerar resumo
    success = generate_summary(args, results)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
